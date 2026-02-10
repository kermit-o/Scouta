import re

with open('main.py', 'r') as f:
    content = f.read()

print("Buscando función register_user incompleta...")

# Patrón para encontrar la función register_user incompleta
# Buscar desde async def register_user hasta donde se corta
pattern = r'(async def register_user\(user: UserCreate, db: AsyncSession = Depends\(get_db\)\):\s*""".*?"""\s*if not DB_AVAILABLE:\s*raise HTTPException\(status_code=503, detail="Database service unavailable"\)\s*try:\s*from sqlalchemy import select\s*from sqlalchemy\.exc import IntegrityError\s*# Verificar si usuario ya existe\s*result = await db\.execute\(\s*select\(User\)\.where\(\s*\(User\.username == user\.username\) \| \(User\.email == user\.email\)\s*\)\s*\)\s*existing_user = result\.scalar_one_or_none\(\)\s*if existing_user:\s*raise HTTPException\(\s*status_code=400,\s*detail="Username or email already registered"\s*\)\s*# Crear nuevo usuario\s*hashed_password = get_password_hash\(user\.password\)\s*new_user = User\(\s*username=user\.username,\s*email=user\.email,\s*full_name=user\.full_name,\s*hashed_password=hashed_password\s*\)\s*db\.add\(new_user\)\s*await db\.commit\(\)\s*await db\.refresh\(new_user\)\s*)(?=\s*except|\s*@app|\Z)'

# Nueva función completa
new_register = '''async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """Registrar nuevo usuario"""
    if not DB_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database service unavailable")
    
    try:
        from sqlalchemy import select
        from sqlalchemy.exc import IntegrityError
        
        # Verificar si usuario ya existe
        result = await db.execute(
            select(User).where(
                (User.username == user.username) | (User.email == user.email)
            )
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Username or email already registered"
            )
        
        # Crear nuevo usuario
        hashed_password = get_password_hash(user.password)
        new_user = User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=hashed_password
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        return UserResponse(
            username=new_user.username,
            email=new_user.email,
            full_name=new_user.full_name
        )
        
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="User already exists")
    except Exception as e:
        await db.rollback()
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")'''

# Reemplazar
new_content = re.sub(pattern, new_register, content, flags=re.DOTALL)

with open('main.py', 'w') as f:
    f.write(new_content)

print("✅ Función register_user completada")
