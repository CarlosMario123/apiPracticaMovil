from fastapi import FastAPI
from src.shared.database import Base, engine
from src.features.usuarios.router import router as usuarios_router
from src.features.productos.router import router as productos_router
from src.config import settings

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Tienda API",
    description="API para gestión de tienda con usuarios y productos",
    version="1.0.0"
)

# Registrar routers
app.include_router(usuarios_router, prefix=settings.API_V1_STR)
app.include_router(productos_router, prefix=settings.API_V1_STR)
