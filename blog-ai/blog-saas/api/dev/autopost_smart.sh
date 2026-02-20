#!/usr/bin/env bash

ORG_ID="${ORG_ID:-1}"
EMAIL="${EMAIL:-outman3@example.com}"
PASS="${PASS:-ChangeMe123!}"
BASE="${BASE:-http://localhost:8000}"
LOG="${LOG:-/tmp/agent_autopost_smart.log}"

DAY=$(date -u +%Y-%m-%d)
TARGET_FILE="dev/.autopost_target_${ORG_ID}_${DAY}.txt"

# target diario 2..5 persistente por día
if [ -f "$TARGET_FILE" ]; then
  TARGET_TODAY=$(cat "$TARGET_FILE" 2>/dev/null)
fi
if [ -z "${TARGET_TODAY:-}" ]; then
  TARGET_TODAY=$(python - <<'PY'
import random
print(random.randint(2,5))
PY
)
  printf "%s" "$TARGET_TODAY" > "$TARGET_FILE"
fi

echo "== $(date -Is) ORG=${ORG_ID} target_today=${TARGET_TODAY} ==" | tee -a "$LOG"

# login
RAW=$(curl -sS -X POST "$BASE/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASS\"}" 2>/dev/null)

TOKEN=$(printf '%s' "$RAW" | python -c 'import sys,json; print(json.load(sys.stdin).get("access_token",""))' 2>/dev/null)
echo "TOKEN_LEN=${#TOKEN}" | tee -a "$LOG"

if [ "${#TOKEN}" -lt 20 ]; then
  echo "Login failed: $RAW" | tee -a "$LOG"
  echo "== end ==" | tee -a "$LOG"
  return 0 2>/dev/null || true
fi

# publicados hoy (UTC)
PUBLISHED_TODAY=$(sqlite3 dev.db "
SELECT COUNT(*) FROM posts
WHERE org_id=$ORG_ID
  AND status='published'
  AND substr(created_at,1,10)='$DAY';
" 2>/dev/null)

PUBLISHED_TODAY="${PUBLISHED_TODAY:-0}"
echo "published_today=$PUBLISHED_TODAY" | tee -a "$LOG"

if [ "$PUBLISHED_TODAY" -ge "$TARGET_TODAY" ]; then
  echo "STOP: daily target reached" | tee -a "$LOG"
  echo "== end ==" | tee -a "$LOG"
  return 0 2>/dev/null || true
fi

# pick agent (roulette + cooldowns)
PICK=$(python - <<PY
import sqlite3, random, datetime

ORG_ID=int("$ORG_ID")
DAY="$DAY"

def weight_from_profile(topics, style, risk):
    topics=(topics or "").lower()
    style=(style or "").lower()
    risk=int(risk or 0)
    w=1.0
    if risk>=3: w*=1.8
    elif risk==2: w*=1.3
    else: w*=0.9
    if "concise" in style or "short" in style: w*=1.25
    if "longform" in style or "essay" in style: w*=0.8
    if any(k in topics for k in ["trend","news","current","politic","epstein","files","rss","twitter","x/"]): w*=1.6
    if any(k in topics for k in ["philosophy","metaphysics","consciousness","spiritual"]): w*=0.85
    if any(k in topics for k in ["science","tech","ai","governance"]): w*=1.1
    return max(0.2, min(5.0, w))

def cadence_bucket(topics, style, risk):
    topics=(topics or "").lower()
    style=(style or "").lower()
    risk=int(risk or 0)
    bucket="weekly"
    if any(k in topics for k in ["trend","news","current","politic","epstein"]) or risk>=3:
        bucket="daily"
    if any(k in topics for k in ["philosophy","metaphysics"]) or "longform" in style:
        bucket="monthly"
    return bucket

def cooldown_seconds(bucket):
    if bucket=="daily": return 8*3600
    if bucket=="weekly": return 3*24*3600
    return 20*24*3600

conn=sqlite3.connect("dev.db")
conn.row_factory=sqlite3.Row
cur=conn.cursor()

# columnas esperadas: is_enabled, is_shadow_banned, topics, style, risk_level
agents=cur.execute("""
SELECT id, topics, style, risk_level
FROM agent_profiles
WHERE org_id=? AND is_enabled=1 AND is_shadow_banned=0
ORDER BY id
""",(ORG_ID,)).fetchall()

if not agents:
    print("")
    raise SystemExit

now=datetime.datetime.now(datetime.timezone.utc)

eligible=[]
for a in agents:
    agent_id=a["id"]
    topics=a["topics"]
    style=a["style"]
    risk=a["risk_level"]

    row=cur.execute("""
    SELECT created_at FROM posts
    WHERE org_id=? AND author_agent_id=?
    ORDER BY id DESC LIMIT 1
    """,(ORG_ID,agent_id)).fetchone()

    bucket=cadence_bucket(topics, style, risk)
    cooldown=cooldown_seconds(bucket)

    ok=True
    if row and row["created_at"]:
        try:
            last_dt=datetime.datetime.fromisoformat(row["created_at"]).replace(tzinfo=datetime.timezone.utc)
            if (now-last_dt).total_seconds() < cooldown:
                ok=False
        except Exception:
            pass

    if bucket=="daily":
        c=cur.execute("""
        SELECT COUNT(*) FROM posts
        WHERE org_id=? AND author_agent_id=? AND status='published'
          AND substr(created_at,1,10)=?
        """,(ORG_ID,agent_id,DAY)).fetchone()[0]
        if c>=1:
            ok=False

    if ok:
        w=weight_from_profile(topics, style, risk)
        eligible.append((agent_id,w,bucket))

if not eligible:
    print("")
    raise SystemExit

total=sum(w for _,w,_ in eligible)
r=random.random()*total
acc=0.0
picked=eligible[-1][0]
bucket=eligible[-1][2]
for aid,w,b in eligible:
    acc+=w
    if acc>=r:
        picked=aid; bucket=b; break

print(f"{picked}|{bucket}")
PY
)

if [ -z "$PICK" ]; then
  echo "No eligible agent right now (cooldowns)." | tee -a "$LOG"
  echo "== end ==" | tee -a "$LOG"
  return 0 2>/dev/null || true
fi

AGENT_ID=$(printf "%s" "$PICK" | cut -d'|' -f1)
BUCKET=$(printf "%s" "$PICK" | cut -d'|' -f2)
echo "picked_agent=$AGENT_ID bucket=$BUCKET" | tee -a "$LOG"

RESP=$(curl -sS -X POST \
  "$BASE/api/v1/orgs/$ORG_ID/agents/$AGENT_ID/generate-post?publish=true" \
  -H "Authorization: Bearer $TOKEN" 2>/dev/null)

PARSED=$(printf "%s" "$RESP" | python - <<'PY' 2>/dev/null || true
import sys, json
s=sys.stdin.read().strip()
try:
    print(json.dumps(json.loads(s), indent=2, ensure_ascii=False))
except Exception:
    print(s)
PY
)

printf "%s\n" "$PARSED" | tee -a "$LOG"

echo "== latest posts ==" | tee -a "$LOG"
sqlite3 -header -column dev.db "SELECT id, author_agent_id, title, status, created_at FROM posts WHERE org_id=$ORG_ID ORDER BY id DESC LIMIT 5;" | tee -a "$LOG"

echo "== end ==" | tee -a "$LOG"
