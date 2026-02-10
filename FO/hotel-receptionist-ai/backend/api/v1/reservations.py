"""
Endpoints para gestión de reservas - Versión 1
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import date
import logging

from services.reservation_service import ReservationService

router = APIRouter(prefix="/api/v1/reservations", tags=["reservations"])
logger = logging.getLogger(__name__)

@router.get("/availability")
async def check_availability(
    check_in: date,
    check_out: date,
    room_type: Optional[str] = Query(None, description="Tipo de habitación")
):
    """
    Verificar disponibilidad de habitaciones
    
    - **check_in**: Fecha de entrada (YYYY-MM-DD)
    - **check_out**: Fecha de salida (YYYY-MM-DD)
    - **room_type**: (Opcional) Tipo de habitación (standard, deluxe, suite)
    """
    try:
        if check_in >= check_out:
            raise HTTPException(
                status_code=400,
                detail="La fecha de entrada debe ser anterior a la de salida"
            )
        
        if (check_out - check_in).days > 30:
            raise HTTPException(
                status_code=400,
                detail="La estadía máxima es de 30 días"
            )
        
        availability = await ReservationService.check_availability(
            check_in, check_out, room_type
        )
        
        return {
            "success": True,
            "data": availability
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verificando disponibilidad: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("")
async def create_reservation(reservation: dict):
    """
    Crear una nueva reserva.
    Acepta room_type (name) o room_type_id (uuid).
    """
    try:
        required_fields = ["guest_name", "guest_email", "check_in", "check_out"]
        for field in required_fields:
            if field not in reservation:
                raise HTTPException(
                    status_code=400,
                    detail=f"Campo requerido faltante: {field}",
                )

        room_type = (reservation.get("room_type") or "").strip()
        room_type_id = (reservation.get("room_type_id") or "").strip()

        # Si room_type no está presente, se intenta usar room_type_id
        if not room_type and room_type_id:
            # Resolver room_type usando room_type_id
            room_type = await ReservationService.resolve_room_type_by_id(room_type_id)

        if not room_type:
            raise HTTPException(
                status_code=400,
                detail="Campo requerido faltante: room_type o room_type_id",
            )

        result = await ReservationService.create_reservation(reservation)

        return {
            "success": True,
            "message": "Reserva creada exitosamente",
            "data": result,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando reserva: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/{reservation_id}")
async def get_reservation(reservation_id: str):
    """Obtener información de una reserva específica"""
    try:
        reservation = await ReservationService.get_reservation(reservation_id)
        
        if not reservation:
            raise HTTPException(
                status_code=404,
                detail=f"Reserva no encontrada: {reservation_id}"
            )
        
        return {
            "success": True,
            "data": reservation
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo reserva: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("")
async def list_reservations(
    status: Optional[str] = Query(None, description="Filtrar por estado"),
    limit: int = Query(50, ge=1, le=100, description="Límite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación")
):
    """Listar reservas desde BD"""
    try:
        data = await ReservationService.list_reservations(
            status=status,
            limit=limit,
            offset=offset,
        )
        return {
            "success": True,
            "data": data,
        }
    except Exception as e:
        logger.error(f"Error listando reservas: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
