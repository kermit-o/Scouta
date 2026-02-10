# diet_ai/backend/services/ai_service.py
import cv2
import numpy as np
from PIL import Image
import io
import tensorflow as tf
from typing import Dict, List, Optional
import requests

class AIDietService:
    def __init__(self):
        # Modelos pre-entrenados (placeholder para integración real)
        self.food_classes = [
            'pizza', 'burger', 'salad', 'pasta', 'rice', 
            'chicken', 'fish', 'vegetables', 'fruit', 'bread'
        ]
    
    async def analyze_food_image(self, image_bytes: bytes) -> Dict:
        """
        Analiza imagen de comida y detecta ingredientes/nutrientes
        """
        try:
            # Convertir bytes a imagen OpenCV
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Preprocesamiento
            img_resized = cv2.resize(img, (224, 224))
            
            # Aquí iría la inferencia del modelo ML
            # Por ahora devolvemos resultados simulados
            
            analysis = {
                "detected_foods": ["chicken", "rice", "vegetables"],
                "confidence_scores": [0.85, 0.90, 0.75],
                "estimated_calories": 650,
                "estimated_macros": {
                    "protein_g": 45,
                    "carbs_g": 75,
                    "fat_g": 20
                },
                "ingredients": ["chicken breast", "white rice", "broccoli", "carrots"],
                "health_score": 8.5  # 1-10
            }
            
            return analysis
            
        except Exception as e:
            raise Exception(f"Error analyzing image: {str(e)}")
    
    async def generate_diet_plan(self, user_profile: Dict) -> Dict:
        """
        Genera plan de dieta personalizado basado en perfil de usuario
        """
        # Calcular necesidades calóricas (fórmula básica)
        bmr = self._calculate_bmr(user_profile)
        daily_calories = self._calculate_daily_calories(bmr, user_profile)
        
        # Calcular macros
        macros = self._calculate_macros(daily_calories, user_profile['goal'])
        
        # Generar plan de comidas
        meal_plan = self._generate_meal_plan(daily_calories, macros, user_profile)
        
        return {
            "daily_calories": daily_calories,
            "macros": macros,
            "meal_plan": meal_plan,
            "shopping_list": self._generate_shopping_list(meal_plan),
            "recommendations": self._get_recommendations(user_profile)
        }
    
    def _calculate_bmr(self, profile: Dict) -> float:
        """Fórmula de Mifflin-St Jeor"""
        if profile['gender'] == 'male':
            bmr = 10 * profile['weight_kg'] + 6.25 * profile['height_cm'] - 5 * profile['age'] + 5
        else:
            bmr = 10 * profile['weight_kg'] + 6.25 * profile['height_cm'] - 5 * profile['age'] - 161
        return bmr
    
    def _calculate_daily_calories(self, bmr: float, profile: Dict) -> float:
        """Ajustar por nivel de actividad"""
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
        
        calories = bmr * activity_multipliers.get(profile['activity_level'], 1.2)
        
        # Ajustar por objetivo
        if profile['goal'] == 'weight_loss':
            calories -= 500  # Déficit de 500 calorías
        elif profile['goal'] == 'muscle_gain':
            calories += 300  # Superávit de 300 calorías
        
        return round(calories)
    
    def _calculate_macros(self, calories: float, goal: str) -> Dict:
        """Calcular distribución de macronutrientes"""
        if goal == 'weight_loss':
            # Alta proteína, moderado carb, bajo grasa
            protein_ratio = 0.35
            carb_ratio = 0.40
            fat_ratio = 0.25
        elif goal == 'muscle_gain':
            # Alta proteína, alta carb, moderada grasa
            protein_ratio = 0.30
            carb_ratio = 0.50
            fat_ratio = 0.20
        else:  # maintenance
            protein_ratio = 0.25
            carb_ratio = 0.50
            fat_ratio = 0.25
        
        return {
            "protein_g": round((calories * protein_ratio) / 4),
            "carbs_g": round((calories * carb_ratio) / 4),
            "fat_g": round((calories * fat_ratio) / 9)
        }