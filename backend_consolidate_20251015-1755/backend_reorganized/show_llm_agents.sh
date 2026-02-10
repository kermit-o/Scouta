#!/usr/bin/env bash
# ============================================================
# Script: show_llm_agents.sh
# Objetivo: listar y mostrar el contenido de los archivos
# implicados en la creación de proyectos LLM-driven
# ============================================================

ROOT_DIR="$(pwd)"
AGENTS_DIR="$ROOT_DIR/core/agents"

FILES_TO_SHOW=(
  "$ROOT_DIR/llm_driven_service.py"
  "$AGENTS_DIR/llm_driven_supervisor.py"
  "$AGENTS_DIR/llm_intake_agent.py"
  "$AGENTS_DIR/llm_planning_agent.py"
  "$AGENTS_DIR/llm_builder_agent.py"
  "$AGENTS_DIR/packager_agent.py"
  "$AGENTS_DIR/real_project_builder_fixed.py"
  "$AGENTS_DIR/supervisor_agent.py"
  "$AGENTS_DIR/dual_pipeline_supervisor.py"
)

OUTPUT_FILE="$ROOT_DIR/llm_agents_dump.txt"

echo "🔍 Recolectando archivos implicados en la generación LLM..."
echo "Salida: $OUTPUT_FILE"
echo "============================================================" > "$OUTPUT_FILE"

for FILE in "${FILES_TO_SHOW[@]}"; do
    if [ -f "$FILE" ]; then
        echo -e "\n\n============================================================" >> "$OUTPUT_FILE"
        echo "📄 FILE: $FILE" >> "$OUTPUT_FILE"
        echo "------------------------------------------------------------" >> "$OUTPUT_FILE"
        cat "$FILE" >> "$OUTPUT_FILE"
    else
        echo "⚠️  No encontrado: $FILE" >> "$OUTPUT_FILE"
    fi
done

echo -e "\n✅ Finalizado. Contenido consolidado en: $OUTPUT_FILE"
