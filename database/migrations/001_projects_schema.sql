-- Schema aligned with backend/app/models/project.py (UUID string ids)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS projects (
  id VARCHAR(36) PRIMARY KEY,
  user_id TEXT NOT NULL,
  project_name TEXT NOT NULL,
  requirements TEXT NOT NULL,
  status TEXT DEFAULT 'pending',
  generated_plan TEXT,
  technology_stack JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS project_artifacts (
  id VARCHAR(36) PRIMARY KEY,
  project_id VARCHAR(36) NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  artifact_type TEXT,
  file_path TEXT,
  content TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE OR REPLACE FUNCTION set_updated_at() RETURNS trigger AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_projects_updated_at') THEN
    CREATE TRIGGER trg_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE PROCEDURE set_updated_at();
  END IF;
END $$;
ALTER TABLE projects ADD COLUMN IF NOT EXISTS result TEXT;
