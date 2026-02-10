#!/usr/bin/env python3
"""
Crear una imagen de prueba para análisis de comida
"""
from PIL import Image, ImageDraw
import os

# Crear una imagen simple de prueba
img = Image.new('RGB', (400, 300), color='green')
draw = ImageDraw.Draw(img)

# Dibujar un "plato" de comida
draw.ellipse([50, 50, 350, 250], outline='white', width=3)
draw.ellipse([100, 100, 300, 200], fill='brown')  # "carne"
draw.rectangle([150, 120, 250, 180], fill='yellow')  # "arroz"
draw.rectangle([120, 80, 180, 100], fill='orange')  # "zanahoria"
draw.rectangle([200, 80, 260, 100], fill='darkgreen')  # "brócoli"

# Guardar
os.makedirs('test_images', exist_ok=True)
img.save('test_images/test_food.jpg')
print("✅ Imagen de prueba creada: test_images/test_food.jpg")
