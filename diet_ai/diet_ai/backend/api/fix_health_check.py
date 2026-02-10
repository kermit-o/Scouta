from sqlalchemy import text

# Reemplazar la función health_check en main.py

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check endpoint"""
    
    # Verificar PostgreSQL
    postgres_status = "unavailable"
    postgres_error = None
    
    if DB_AVAILABLE and engine is not None:
        try:
            async with engine.begin() as conn:
                # Usar text() para la consulta SQL
                result = await conn.execute(text("SELECT 1"))
                # Verificar que devolvió algo
                row = result.fetchone()
                if row and row[0] == 1:
                    postgres_status = "healthy"
                else:
                    postgres_status = "unhealthy"
                    postgres_error = "Unexpected query result"
        except Exception as e:
            postgres_status = "unhealthy"
            postgres_error = str(e)
    else:
        postgres_status = "unavailable"
        postgres_error = "Database configuration not loaded"
    
    # Verificar Redis
    redis_status = "unavailable"
    redis_error = None
    
    if REDIS_AVAILABLE and redis_client is not None:
        try:
            redis_client.ping()
            redis_status = "healthy"
        except Exception as e:
            redis_status = "unhealthy"
            redis_error = str(e)
    else:
        redis_status = "unavailable"
        redis_error = "Redis configuration not loaded"
    
    # Determinar estado general
    overall_status = "healthy"
    if postgres_status != "healthy" or redis_status != "healthy":
        overall_status = "degraded"
    
    response_data = {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "services": {
            "postgres": {"status": postgres_status},
            "redis": {"status": redis_status},
            "api": "healthy"
        }
    }
    
    # Agregar errores si existen
    if postgres_error:
        response_data["services"]["postgres"]["error"] = postgres_error
    if redis_error:
        response_data["services"]["redis"]["error"] = redis_error
    
    return HealthResponse(**response_data)
