# Reemplazar la función health_check en main.py con esta versión mejorada

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check endpoint"""
    
    # Verificar PostgreSQL con timeout
    postgres_status = "checking"
    postgres_error = None
    
    if DB_AVAILABLE and engine is not None:
        try:
            import asyncio
            
            # Usar timeout para no bloquear
            async def test_postgres():
                async with engine.begin() as conn:
                    result = await conn.execute("SELECT 1, version()")
                    return True
            
            # Ejecutar con timeout de 5 segundos
            try:
                await asyncio.wait_for(test_postgres(), timeout=5.0)
                postgres_status = "healthy"
            except asyncio.TimeoutError:
                postgres_status = "timeout"
                postgres_error = "Connection timeout"
            except Exception as e:
                postgres_status = "unhealthy"
                postgres_error = str(e)
                
        except Exception as e:
            postgres_status = "error"
            postgres_error = str(e)
    else:
        postgres_status = "unavailable"
        postgres_error = "Database configuration not loaded"
    
    # Verificar Redis
    redis_status = "checking"
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
    if postgres_status in ["unhealthy", "error"] or redis_status == "unhealthy":
        overall_status = "unhealthy"
    
    response_data = {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "services": {
            "postgres": {
                "status": postgres_status,
                "error": postgres_error
            } if postgres_error else {"status": postgres_status},
            "redis": {
                "status": redis_status,
                "error": redis_error
            } if redis_error else {"status": redis_status},
            "api": "healthy"
        }
    }
    
    # Log para debugging
    if overall_status != "healthy":
        logger.warning(f"Health check: {overall_status}. PostgreSQL: {postgres_status}, Redis: {redis_status}")
    
    return response_data
