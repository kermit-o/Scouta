from setuptools import setup, find_packages

setup(
    name="dietai-backend",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "sqlalchemy==2.0.23",
        "psycopg2-binary==2.9.9",
        "python-jose[cryptography]==3.3.0",
        "passlib[bcrypt]==1.7.4",
        "pydantic==2.5.0",
        "pydantic-settings==2.1.0",
        "python-dotenv==1.0.0",
        "pillow==10.1.0",
        "numpy==1.24.3",
    ],
)
