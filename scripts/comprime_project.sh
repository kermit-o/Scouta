zip -r project_backup_$(date +"%Y%m%d_%H%M%S").zip . -x "*.git*" "*__pycache__*" "*.DS_Store*" "*.pytest_cache*" "*.mypy_cache*" "*.venv*" "venv/*" "env/*"
