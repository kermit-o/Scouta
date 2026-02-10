"""
Rate limiting SIMPLIFICADO - Sin slowapi
"""

# Mock limiter que no hace nada (para desarrollo)
class MockLimiter:
    def __init__(self, key_func=None):
        self.key_func = key_func
    
    def limit(self, *args, **kwargs):
        # Decorador que no hace nada
        def decorator(func):
            return func
        return decorator

# Instancia mock
limiter = MockLimiter()

print("INFO: Using mock rate limiter for development")
