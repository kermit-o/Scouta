-- ============================================
-- GEOLOCALIZACIÓN: PostGIS + coords en jobs
-- ============================================
CREATE EXTENSION IF NOT EXISTS postgis;

-- Agrega columnas de ubicación a jobs
ALTER TABLE public.jobs
  ADD COLUMN IF NOT EXISTS latitude  DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS longitude DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS location  GEOGRAPHY(POINT, 4326);

-- Índice espacial para búsquedas rápidas
CREATE INDEX IF NOT EXISTS jobs_location_idx ON public.jobs USING GIST(location);

-- Trigger: auto-genera geography desde lat/lng
CREATE OR REPLACE FUNCTION public.sync_job_location()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.latitude IS NOT NULL AND NEW.longitude IS NOT NULL THEN
    NEW.location = ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326)::geography;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER jobs_sync_location
  BEFORE INSERT OR UPDATE ON public.jobs
  FOR EACH ROW EXECUTE FUNCTION public.sync_job_location();

-- Agrega coords a users (ubicación del pro)
ALTER TABLE public.users
  ADD COLUMN IF NOT EXISTS latitude  DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS longitude DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS location  GEOGRAPHY(POINT, 4326);

CREATE INDEX IF NOT EXISTS users_location_idx ON public.users USING GIST(location);

CREATE TRIGGER users_sync_location
  BEFORE INSERT OR UPDATE ON public.users
  FOR EACH ROW EXECUTE FUNCTION public.sync_job_location();

-- ============================================
-- FUNCIÓN: jobs cercanos por radio (km)
-- ============================================
CREATE OR REPLACE FUNCTION public.jobs_nearby(
  lat DOUBLE PRECISION,
  lng DOUBLE PRECISION,
  radius_km DOUBLE PRECISION DEFAULT 25,
  max_results INT DEFAULT 50
)
RETURNS TABLE (
  id UUID, title TEXT, description TEXT, category job_category,
  status job_status, budget_min NUMERIC, budget_max NUMERIC,
  currency supported_currency, country supported_country,
  city TEXT, is_remote BOOLEAN, latitude DOUBLE PRECISION,
  longitude DOUBLE PRECISION, distance_km DOUBLE PRECISION,
  created_at TIMESTAMPTZ
) AS $$
  SELECT
    j.id, j.title, j.description, j.category,
    j.status, j.budget_min, j.budget_max,
    j.currency, j.country, j.city, j.is_remote,
    j.latitude, j.longitude,
    ROUND((ST_Distance(j.location, ST_SetSRID(ST_MakePoint(lng, lat), 4326)::geography) / 1000)::numeric, 2) AS distance_km,
    j.created_at
  FROM public.jobs j
  WHERE
    j.status = 'open'
    AND j.location IS NOT NULL
    AND ST_DWithin(
      j.location,
      ST_SetSRID(ST_MakePoint(lng, lat), 4326)::geography,
      radius_km * 1000
    )
  ORDER BY distance_km ASC
  LIMIT max_results;
$$ LANGUAGE sql STABLE;
