# backend/services/weather.py
async def get_weather_forecast():
    """Obtener pronóstico del tiempo"""
    # Podría integrarse con OpenWeatherMap
    return {
        "today": "Soleado, 25°C",
        "tomorrow": "Parcialmente nublado, 23°C"
    }