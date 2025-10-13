"""Add missing project columns"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql 

# revision identifiers, used by Alembic.
revision = '731f548685d5'
down_revision = 'jobs_agent_runs_artifacts_0001'
branch_labels = None
depends_on = None

def upgrade():
    # --- AGENT_RUNS_ID_UUID_HARDFIX ---    

    conn = op.get_bind()

    # 0) Si ya es uuid, salimos
    row = conn.execute(sa.text(
        "SELECT data_type FROM information_schema.columns "
        "WHERE table_name='agent_runs' AND column_name='id'"
    )).fetchone()
    if row and str(row[0]).lower() == 'uuid':
        pass
    else:
        # 1) Intento directo con USING
        try:
            conn.execute(sa.text(
                "ALTER TABLE agent_runs ALTER COLUMN id TYPE uuid USING id::uuid"
            ))
        except Exception:
            # 2) Plan B: columna nueva, PK nueva, rename, sin extensiones
            conn.execute(sa.text("ALTER TABLE agent_runs ADD COLUMN id_new uuid"))
            # uuid sin extensiones: md5(random()||clock_timestamp())::uuid
            conn.execute(sa.text(
                "UPDATE agent_runs "
                "SET id_new = md5(random()::text || clock_timestamp()::text)::uuid"
            ))
            # localizar y dropear PK actual
            pkname = conn.execute(sa.text("""
                SELECT conname
                FROM pg_constraint
                WHERE conrelid = 'agent_runs'::regclass AND contype = 'p'
            """)).scalar()
            if pkname:
                conn.execute(sa.text('ALTER TABLE agent_runs DROP CONSTRAINT "' + pkname + '"'))
            # nueva PK y NO NULL
            conn.execute(sa.text("ALTER TABLE agent_runs ALTER COLUMN id_new SET NOT NULL"))
            conn.execute(sa.text("ALTER TABLE agent_runs ADD PRIMARY KEY (id_new)"))
            # reemplazo de columna
            conn.execute(sa.text("ALTER TABLE agent_runs DROP COLUMN id"))
            conn.execute(sa.text("ALTER TABLE agent_runs RENAME COLUMN id_new TO id"))
    # --- END AGENT_RUNS_ID_UUID_HARDFIX ---


    # --- BEGIN ORIGINAL (filtered) ---
    # --- AGENT_RUNS_ID_UUID_PATCH ---
        # Habilitar pgcrypto (si existe en PG alpine, es segura)
        op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
        # Intento directo con USING
        try:
            op.execute("ALTER TABLE agent_runs ALTER COLUMN id TYPE uuid USING id::uuid")
        except Exception:
            # Plan B: nueva columna UUID, mover PK y renombrar
            op.execute("ALTER TABLE agent_runs ADD COLUMN id_new uuid DEFAULT gen_random_uuid()")
            op.execute("ALTER TABLE agent_runs DROP CONSTRAINT IF EXISTS agent_runs_pkey")
            op.execute("ALTER TABLE agent_runs ADD PRIMARY KEY (id_new)")
            op.drop_column('agent_runs', 'id')
            op.alter_column('agent_runs', 'id_new', new_column_name='id')
            op.execute("ALTER TABLE agent_runs ALTER COLUMN id DROP DEFAULT")
        # --- END AGENT_RUNS_ID_UUID_PATCH ---
        # Hemos eliminado TEMPORALMENTE toda la lógica de alteración de columnas (op.alter_column)
        # y SOLAMENTE estamos aplicando la adición de las columnas faltantes en la tabla 'projects'
                
        # CAMBIOS EN LA TABLA PROJECTS (Las columnas faltantes) - Objetivo Principal
        op.add_column('projects', sa.Column('requirements', sa.JSON(), nullable=True))
        op.add_column('projects', sa.Column('plan_json', sa.JSON(), nullable=True))
        op.add_column('projects', sa.Column('generated_plan', sa.Text(), nullable=True))
        op.add_column('projects', sa.Column('technology_stack', sa.JSON(), nullable=True))
        op.add_column('projects', sa.Column('result', sa.JSON(), nullable=True))
        op.add_column('projects', sa.Column('status', sa.Enum('pending', 'planning', 'executing', 'testing', 'finished', 'failed', name='projectstatus'), server_default='pending', nullable=True))
        op.add_column('projects', sa.Column('artifact_path', sa.String(length=255), nullable=True))
        op.add_column('projects', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
                                                

# --- END ORIGINAL (filtered) ---
def downgrade():
    op.drop_column('projects', 'updated_at')
    op.drop_column('projects', 'artifact_path')
    op.drop_column('projects', 'status')
    op.drop_column('projects', 'result')
    op.drop_column('projects', 'technology_stack')
    op.drop_column('projects', 'generated_plan')
    op.drop_column('projects', 'plan_json')
    op.drop_column('projects', 'requirements')