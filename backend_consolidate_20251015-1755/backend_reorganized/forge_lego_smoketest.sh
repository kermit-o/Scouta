#!/usr/bin/env bash
set -e

echo "=== Forge Lego Smoke Test ==="
echo "Workdir: $(pwd)"

echo
echo "===> 1) Generando desde requisitos (products + orders)..."
curl -s -X POST "http://localhost:8000/api/forge/generate_from_requirements" \
  -H "Content-Type: application/json" \
  -d '{"requirements_text": "Quiero un ecommerce con catálogo de productos y checkout con órdenes y pagos."}' \
  | python -m json.tool

echo
echo "===> 2) Estructura de workdir/from_requirements (nivel 3)..."
find workdir/from_requirements -maxdepth 3 -type d -print | sed 's/^/ - /'

echo
echo "===> 3) Listando archivos generados para Product..."
ls -1 workdir/from_requirements/business_ecommerce_product_catalog/products || echo "No product files."

echo
echo "===> 4) Listando archivos generados para Order..."
ls -1 workdir/from_requirements/business_ecommerce_order_management/orders || echo "No order files."

echo
echo "===> 5) Smoke test de endpoints generados (puede devolver 422/500 si no hay DB, es solo conectividad)"

echo
echo "--> GET /api/products/"
curl -i "http://localhost:8000/api/products/" || echo "(error de conexión)"

echo
echo "--> GET /api/orders/"
curl -i "http://localhost:8000/api/orders/" || echo "(error de conexión)"

echo
echo "=== Smoke test terminado. Revisa arriba respuestas HTTP y posibles errores de FastAPI/SQLAlchemy."
