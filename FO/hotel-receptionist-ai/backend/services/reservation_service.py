"""
Servicio para gestión de reservas (DB real) - asyncpg
Compatible con:
- guests(id, first_name, last_name, email UNIQUE, phone_number, country, language_preference, created_at, updated_at)
- room_types(id, name, description, base_price, max_guests, amenities, available_count, image_url, created_at)
- reservations(id, guest_id, room_type, check_in_date, check_out_date, number_of_guests, special_requests, status, total_price, payment_status, created_at)
"""
from __future__ import annotations

import os
import uuid
import logging
from datetime import date, datetime, time
from typing import Any, Dict, Optional, List, Tuple

import asyncpg
from fastapi import HTTPException

logger = logging.getLogger(__name__)


def _db_dsn() -> str:
    raw = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://hotel_admin:hotel_password@postgres:5432/hotel_db",
    )
    return raw.replace("+asyncpg", "")


def _to_dt(d: date, end_of_day: bool = False) -> datetime:
    # Schema uses "timestamp without time zone" => store naive datetime
    return datetime.combine(d, time(23, 59, 59) if end_of_day else time(0, 0, 0))


def _split_name(full: str) -> Tuple[str, str]:
    s = (full or "").strip()
    if not s:
        return ("Guest", "Unknown")
    parts = [p for p in s.split() if p.strip()]
    if len(parts) == 1:
        return (parts[0], "Unknown")
    return (parts[0], " ".join(parts[1:]))


def _normalize_room_type_name(room_type: str) -> str:
    # Store consistent "room_type" in reservations
    return (room_type or "").strip().lower()


class ReservationService:
    @staticmethod
    async def _find_or_create_guest(conn: asyncpg.Connection, payload: Dict[str, Any]) -> str:
        """
        Resolve guest_id.
        Priority:
          1) guest_id in payload
          2) lookup by email (unique)
          3) create new guest (email required by schema)
        """
        guest_id = (payload.get("guest_id") or "").strip()
        if guest_id:
            return guest_id

        guest_email = (payload.get("guest_email") or "").strip().lower()
        if not guest_email:
            raise ValueError("guest_email is required to create/resolve guest (guests.email is NOT NULL and UNIQUE)")

        row = await conn.fetchrow("SELECT id FROM guests WHERE email = $1 LIMIT 1", guest_email)
        if row:
            return str(row["id"])

        guest_phone = (payload.get("guest_phone") or "").strip()
        if not guest_phone:
            # phone_number is NOT NULL
            guest_phone = "+0000000000"

        first_name, last_name = _split_name(payload.get("guest_name") or "")
        country = (payload.get("country") or None)
        language = (payload.get("language_preference") or None)  # default in DB is 'es'

        new_id = str(uuid.uuid4())
        await conn.execute(
            """
            INSERT INTO guests (id, first_name, last_name, email, phone_number, country, language_preference)
            VALUES ($1, $2, $3, $4, $5, $6, COALESCE($7, 'es'))
            """,
            new_id,
            first_name,
            last_name,
            guest_email,
            guest_phone,
            country,
            language,
        )
        return new_id
    @staticmethod
    async def resolve_room_type_by_id(room_type_id: str) -> str:
        """Resolve room type name from room_types.id (UUID)."""
        key = (room_type_id or "").strip()
        if not key:
            raise ValueError("room_type_id is required")

        conn = await asyncpg.connect(_db_dsn())  # Conexión a la base de datos
        try:
            logger.info(f"Resolviendo tipo de habitación para el ID: {key}")
            name = await conn.fetchval(
                "SELECT name FROM room_types WHERE id = $1", key
            )
            if not name:
                logger.error(f"No se encontró room_type para el ID: {key}")
                raise ValueError(f"room_type not found for id: {key}")
            logger.info(f"Tipo de habitación resuelto: {name}")
            return str(name)
        finally:
            await conn.close()

    @staticmethod
    async def _resolve_room_type(conn: asyncpg.Connection, room_type: str) -> asyncpg.Record:
        """
        Resolve a room type by name (case-insensitive).
        Because your table contains duplicates, we select with this priority:
          1) available_count > 0
          2) newest created_at
        """
        key = (room_type or "").strip().lower()
        if not key:
            raise ValueError("room_type is required")

        row = await conn.fetchrow(
            """
            SELECT id, name, description, base_price, max_guests, amenities, available_count, image_url, created_at
            FROM room_types
            WHERE lower(name) = $1
            ORDER BY (available_count > 0) DESC, created_at DESC
            LIMIT 1
            """,
            key,
        )
        if not row:
            raise ValueError(f"room_type not found by name: {room_type}")
        return row

    @staticmethod
    async def check_availability(
        check_in: date,
        check_out: date,
        room_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Availability model per room type name:
          available_count - overlapping reservations count
        Overlap:
          check_in_date < requested_check_out AND check_out_date > requested_check_in
        """
        conn = await asyncpg.connect(_db_dsn())
        try:
            ci = _to_dt(check_in, end_of_day=False)
            co = _to_dt(check_out, end_of_day=False)

            if room_type:
                rt = await ReservationService._resolve_room_type(conn, room_type)
                rt_name_norm = _normalize_room_type_name(rt["name"])
                capacity = int(rt.get("available_count") or 0)

                booked = await conn.fetchval(
                    """
                    SELECT COUNT(*)
                    FROM reservations
                    WHERE lower(room_type) = $1
                      AND COALESCE(status,'confirmed') IN ('confirmed','checked_in')
                      AND check_in_date < $3
                      AND check_out_date > $2
                    """,
                    rt_name_norm,
                    ci,
                    co,
                )
                booked = int(booked or 0)
                available_units = max(0, capacity - booked)

                return {
                    "check_in": check_in.isoformat(),
                    "check_out": check_out.isoformat(),
                    "available": available_units > 0,
                    "room_type": {
                        "id": str(rt.get("id")),
                        "name": rt.get("name"),
                        "description": rt.get("description"),
                        "base_price": float(rt.get("base_price") or 0),
                        "max_guests": int(rt.get("max_guests") or 0),
                        "amenities": rt.get("amenities"),
                        "available_count": capacity,
                        "booked": booked,
                        "available_units": available_units,
                    },
                    "total_nights": (check_out - check_in).days,
                }

            rows = await conn.fetch(
                """
                SELECT id, name, description, base_price, max_guests, amenities, available_count, image_url, created_at
                FROM room_types
                ORDER BY lower(name), created_at DESC
                """
            )

            # Consolidate duplicates by name using "best" record (available_count>0 then newest)
            best_by_name: Dict[str, asyncpg.Record] = {}
            for r in rows:
                name_key = (r.get("name") or "").strip().lower()
                if not name_key:
                    continue
                cur = best_by_name.get(name_key)
                if cur is None:
                    best_by_name[name_key] = r
                    continue
                # choose higher priority
                cur_av = int(cur.get("available_count") or 0)
                r_av = int(r.get("available_count") or 0)
                if (r_av > 0 and cur_av <= 0) or (r_av == cur_av and (r.get("created_at") or datetime.min) > (cur.get("created_at") or datetime.min)):
                    best_by_name[name_key] = r

            results: List[Dict[str, Any]] = []
            any_available = False

            for name_key, rt in sorted(best_by_name.items(), key=lambda kv: kv[0]):
                rt_name_norm = _normalize_room_type_name(rt["name"])
                capacity = int(rt.get("available_count") or 0)

                booked = await conn.fetchval(
                    """
                    SELECT COUNT(*)
                    FROM reservations
                    WHERE lower(room_type) = $1
                      AND COALESCE(status,'confirmed') IN ('confirmed','checked_in')
                      AND check_in_date < $3
                      AND check_out_date > $2
                    """,
                    rt_name_norm,
                    ci,
                    co,
                )
                booked = int(booked or 0)
                available_units = max(0, capacity - booked)
                available = available_units > 0
                any_available = any_available or available

                results.append({
                    "id": str(rt.get("id")),
                    "name": rt.get("name"),
                    "description": rt.get("description"),
                    "base_price": float(rt.get("base_price") or 0),
                    "max_guests": int(rt.get("max_guests") or 0),
                    "amenities": rt.get("amenities"),
                    "available_count": capacity,
                    "booked": booked,
                    "available_units": available_units,
                    "available": available,
                })

            return {
                "check_in": check_in.isoformat(),
                "check_out": check_out.isoformat(),
                "available": any_available,
                "room_types": results,
                "total_nights": (check_out - check_in).days,
            }
        finally:
            await conn.close()

    @staticmethod
    async def create_reservation(reservation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create reservation in DB.
        Accepts:
          guest_name, guest_email, guest_phone
          check_in, check_out (YYYY-MM-DD)
          room_type (name)
          number_of_guests OR guests
          special_requests (optional)
        """
        room_type = (reservation_data.get("room_type") or "").strip()
        if not room_type:
            raise ValueError("room_type is required")

        check_in = reservation_data.get("check_in")
        check_out = reservation_data.get("check_out")
        if isinstance(check_in, str):
            check_in = date.fromisoformat(check_in)
        if isinstance(check_out, str):
            check_out = date.fromisoformat(check_out)

        if not isinstance(check_in, date) or not isinstance(check_out, date):
            raise ValueError("check_in/check_out must be YYYY-MM-DD")
        if check_in >= check_out:
            raise ValueError("check_in must be before check_out")

        number_of_guests = int(reservation_data.get("number_of_guests") or reservation_data.get("guests") or 1)
        special_requests = (reservation_data.get("special_requests") or "").strip() or None

        nights = (check_out - check_in).days
        ci_dt = _to_dt(check_in, end_of_day=False)
        co_dt = _to_dt(check_out, end_of_day=False)

        conn = await asyncpg.connect(_db_dsn())
        # Accept room_type_id as alternative to room_type
        room_type_id = (reservation_data.get('room_type_id') or '').strip()
        room_type = (reservation_data.get('room_type') or '').strip()
        if room_type_id and not room_type:
            row = await conn.fetchrow('SELECT name FROM room_types WHERE id = $1 LIMIT 1', room_type_id)
            if not row:
                raise ValueError('room_type not found by id')
            reservation_data['room_type'] = str(row['name'])
        try:
            rt = await ReservationService._resolve_room_type(conn, room_type)

            max_guests = int(rt.get("max_guests") or 0)
            if max_guests and number_of_guests > max_guests:
                raise ValueError(f"number_of_guests exceeds max_guests for {rt.get('name')} ({max_guests})")

            base_price = float(rt.get("base_price") or 0)
            total_price = round(base_price * nights, 2)

            guest_id = await ReservationService._find_or_create_guest(conn, reservation_data)

            rid = str(uuid.uuid4())
            stored_room_type = _normalize_room_type_name(rt.get("name") or room_type)

            row = await conn.fetchrow(
                """
                INSERT INTO reservations (
                  id, guest_id, room_type,
                  check_in_date, check_out_date,
                  number_of_guests, special_requests,
                  status, total_price, payment_status
                )
                VALUES (
                  $1, $2, $3,
                  $4, $5,
                  $6, $7,
                  'confirmed', $8, 'pending'
                )
                RETURNING id, guest_id, room_type, check_in_date, check_out_date,
                          number_of_guests, special_requests, status, total_price, payment_status, created_at
                """,
                rid,
                guest_id,
                stored_room_type,
                ci_dt,
                co_dt,
                number_of_guests,
                special_requests,
                total_price,
            )

            return {
                "id": str(row["id"]),
                "status": row.get("status") or "confirmed",
                "payment_status": row.get("payment_status") or "pending",
                "guest_id": str(row["guest_id"]),
                "room_type": row.get("room_type"),
                "check_in_date": str(row.get("check_in_date")),
                "check_out_date": str(row.get("check_out_date")),
                "number_of_guests": int(row.get("number_of_guests") or 1),
                "special_requests": row.get("special_requests"),
                "total_price": float(row.get("total_price") or 0),
                "created_at": str(row.get("created_at")),
                "message": "Reserva creada exitosamente. Recibirá un email de confirmación.",
            }
        finally:
            await conn.close()

    @staticmethod
    async def get_reservation(reservation_id: str) -> Optional[Dict[str, Any]]:
        conn = await asyncpg.connect(_db_dsn())
        try:
            row = await conn.fetchrow(
                """
                SELECT
                  r.id, r.room_type, r.check_in_date, r.check_out_date,
                  r.number_of_guests, r.special_requests,
                  r.status, r.total_price, r.payment_status, r.created_at,
                  g.id as guest_id,
                  g.first_name as guest_first_name,
                  g.last_name as guest_last_name,
                  g.email as guest_email,
                  g.phone_number as guest_phone_number,
                  g.language_preference as guest_language_preference
                FROM reservations r
                JOIN guests g ON g.id = r.guest_id
                WHERE r.id = $1
                """,
                reservation_id,
            )
            return dict(row) if row else None
        finally:
            await conn.close()

    @staticmethod
    async def list_reservations(status: Optional[str] = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        conn = await asyncpg.connect(_db_dsn())
        try:
            if status:
                total = await conn.fetchval("SELECT COUNT(*) FROM reservations WHERE status = $1", status)
                rows = await conn.fetch(
                    """
                    SELECT
                      r.id, r.room_type, r.check_in_date, r.check_out_date,
                      r.number_of_guests, r.status, r.total_price, r.payment_status, r.created_at,
                      g.first_name as guest_first_name,
                      g.last_name as guest_last_name,
                      g.email as guest_email,
                      g.phone_number as guest_phone_number
                    FROM reservations r
                    JOIN guests g ON g.id = r.guest_id
                    WHERE r.status = $1
                    ORDER BY r.created_at DESC
                    LIMIT $2 OFFSET $3
                    """,
                    status, limit, offset
                )
            else:
                total = await conn.fetchval("SELECT COUNT(*) FROM reservations")
                rows = await conn.fetch(
                    """
                    SELECT
                      r.id, r.room_type, r.check_in_date, r.check_out_date,
                      r.number_of_guests, r.status, r.total_price, r.payment_status, r.created_at,
                      g.first_name as guest_first_name,
                      g.last_name as guest_last_name,
                      g.email as guest_email,
                      g.phone_number as guest_phone_number
                    FROM reservations r
                    JOIN guests g ON g.id = r.guest_id
                    ORDER BY r.created_at DESC
                    LIMIT $1 OFFSET $2
                    """,
                    limit, offset
                )

            return {
                "reservations": [dict(r) for r in rows],
                "total": int(total or 0),
                "limit": int(limit),
                "offset": int(offset),
                "status_filter": status,
            }
        finally:
            await conn.close()
