from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict
import io
from PIL import Image
import numpy as np

router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/analyze-food")
async def analyze_food_image(file: UploadFile = File(...)):
    """Analizar imagen de comida usando IA"""
    
    # Verificar que sea una imagen
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image"
        )
    
    # Leer imagen
    contents = await file.read()
    
    try:
        # Convertir a PIL Image
        image = Image.open(io.BytesIO(contents))
        
        # Convertir a numpy array (simulación)
        img_array = np.array(image)
        
        # En una implementación real, aquí procesaríamos con un modelo ML
        # Por ahora devolvemos análisis simulado
        
        analysis = {
            "detected_foods": ["chicken", "rice", "broccoli"],
            "confidence_scores": [0.85, 0.90, 0.75],
            "estimated_calories": 650,
            "estimated_macros": {
                "protein_g": 45,
                "carbs_g": 75,
                "fat_g": 20
            },
            "ingredients": ["chicken breast", "white rice", "broccoli", "garlic"],
            "health_score": 8.5,
            "suggestions": [
                "Buena fuente de proteína",
                "Considera agregar más vegetales coloridos",
                "Porción adecuada para una comida principal"
            ]
        }
        
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "size_bytes": len(contents),
            "dimensions": f"{image.width}x{image.height}",
            "analysis": analysis
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )

@router.post("/analyze-inventory")
async def analyze_inventory_image(file: UploadFile = File(...)):
    """Analizar imagen de inventario/despensa"""
    
    # Simulación similar a analyze_food_image
    contents = await file.read()
    
    return {
        "filename": file.filename,
        "detected_items": [
            {"item": "apples", "quantity": 5, "confidence": 0.95},
            {"item": "eggs", "quantity": 12, "confidence": 0.90},
            {"item": "bread", "quantity": 1, "confidence": 0.85},
            {"item": "milk", "quantity": 1, "confidence": 0.80}
        ],
        "suggestions": [
            "Los huevos expiran en 7 días",
            "Considera comprar más vegetales verdes",
            "La leche se acabará pronto"
        ]
    }
