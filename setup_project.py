import os
import sys
from typing import Dict

class ProjectSetup:
    def __init__(self):
        self.directories = [
            "src",
            "src/shared",
            "src/features",
            "src/features/usuarios",
            "src/features/productos",
        ]
        
        self.requirements = """fastapi==0.109.1
uvicorn==0.27.0
sqlalchemy==2.0.25
pydantic==2.5.3
pydantic-settings==2.1.0
pydantic[email]==2.5.3
python-multipart==0.0.6
python-jose==3.3.0
passlib==1.7.4
bcrypt==4.1.2
alembic==1.13.1
"""

        self.files: Dict[str, str] = {
            "src/config.py": """from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./tienda.db"
    API_V1_STR: str = "/api/v1"

settings = Settings()
""",

            "src/main.py": """from fastapi import FastAPI
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
""",

            "src/shared/database.py": """from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # Solo para SQLite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""",

            "src/shared/exceptions.py": """from fastapi import HTTPException
from typing import Any

class NotFoundError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=404, detail=detail)

class BadRequestError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)

class UnauthorizedError(HTTPException):
    def __init__(self, detail: str = "No autorizado"):
        super().__init__(status_code=401, detail=detail)
""",

            "src/features/usuarios/models.py": """from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from src.shared.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    activo = Column(Boolean, default=True)

    productos = relationship("Producto", back_populates="usuario", cascade="all, delete-orphan")
""",

            "src/features/usuarios/schemas.py": """from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UsuarioBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    email: EmailStr

class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=6)

class Usuario(UsuarioBase):
    id: int
    fecha_registro: datetime
    activo: bool

    class Config:
        from_attributes = True
""",

            "src/features/usuarios/service.py": """from sqlalchemy.orm import Session
from src.shared.exceptions import NotFoundError, BadRequestError
from . import models, schemas
from passlib.context import CryptContext
from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UsuarioService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, usuario: schemas.UsuarioCreate) -> models.Usuario:
        if self.get_by_email(usuario.email):
            raise BadRequestError("Email ya registrado")

        hashed_password = pwd_context.hash(usuario.password)
        db_usuario = models.Usuario(
            nombre=usuario.nombre,
            email=usuario.email,
            password=hashed_password
        )
        
        self.db.add(db_usuario)
        self.db.commit()
        self.db.refresh(db_usuario)
        return db_usuario

    def get_by_id(self, usuario_id: int) -> models.Usuario:
        usuario = self.db.query(models.Usuario).filter(
            models.Usuario.id == usuario_id,
            models.Usuario.activo == True
        ).first()
        if not usuario:
            raise NotFoundError("Usuario no encontrado")
        return usuario

    def get_by_email(self, email: str) -> Optional[models.Usuario]:
        return self.db.query(models.Usuario).filter(
            models.Usuario.email == email,
            models.Usuario.activo == True
        ).first()
""",

            "src/features/usuarios/router.py": """from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from src.shared.database import get_db
from . import schemas, service
from typing import List

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

@router.post("/", response_model=schemas.Usuario, status_code=status.HTTP_201_CREATED)
def create_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    usuario_service = service.UsuarioService(db)
    return usuario_service.create(usuario)

@router.get("/{usuario_id}", response_model=schemas.Usuario)
def get_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario_service = service.UsuarioService(db)
    return usuario_service.get_by_id(usuario_id)
""",

            "src/features/productos/models.py": """from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from src.shared.database import Base

class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(String(500))
    precio = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    activo = Column(Boolean, default=True)

    usuario = relationship("Usuario", back_populates="productos")
""",

            "src/features/productos/schemas.py": """from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ProductoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=200)
    descripcion: Optional[str] = Field(None, max_length=500)
    precio: float = Field(..., gt=0)
    stock: int = Field(0, ge=0)

class ProductoCreate(ProductoBase):
    usuario_id: int

class Producto(ProductoBase):
    id: int
    usuario_id: int
    fecha_creacion: datetime
    activo: bool

    class Config:
        from_attributes = True
""",

            "src/features/productos/service.py": """from sqlalchemy.orm import Session
from src.shared.exceptions import NotFoundError
from . import models, schemas
from ..usuarios.models import Usuario
from typing import List

class ProductoService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, producto: schemas.ProductoCreate) -> models.Producto:
        if not self.db.query(Usuario).filter(
            Usuario.id == producto.usuario_id,
            Usuario.activo == True
        ).first():
            raise NotFoundError("Usuario no encontrado")

        db_producto = models.Producto(**producto.model_dump())
        self.db.add(db_producto)
        self.db.commit()
        self.db.refresh(db_producto)
        return db_producto

    def get_by_usuario(self, usuario_id: int) -> List[models.Producto]:
        productos = self.db.query(models.Producto).filter(
            models.Producto.usuario_id == usuario_id,
            models.Producto.activo == True
        ).all()
        if not productos:
            raise NotFoundError(f"No se encontraron productos para el usuario {usuario_id}")
        return productos
""",

            "src/features/productos/router.py": """from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from src.shared.database import get_db
from . import schemas, service

router = APIRouter(prefix="/productos", tags=["productos"])

@router.post("/", response_model=schemas.Producto, status_code=status.HTTP_201_CREATED)
def create_producto(producto: schemas.ProductoCreate, db: Session = Depends(get_db)):
    producto_service = service.ProductoService(db)
    return producto_service.create(producto)

@router.get("/usuario/{usuario_id}", response_model=List[schemas.Producto])
def get_productos_usuario(usuario_id: int, db: Session = Depends(get_db)):
    producto_service = service.ProductoService(db)
    return producto_service.get_by_usuario(usuario_id)
"""
        }

    def create_directories(self):
        """Crear estructura de directorios y archivos __init__.py"""
        for directory in self.directories:
            os.makedirs(directory, exist_ok=True)
            with open(os.path.join(directory, "__init__.py"), "w") as f:
                pass

    def create_requirements(self):
        """Crear archivo requirements.txt"""
        with open("requirements.txt", "w") as f:
            f.write(self.requirements)

    def create_project_files(self):
        """Crear archivos del proyecto"""
        for file_path, content in self.files.items():
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

    def setup(self):
        """Ejecutar toda la configuración del proyecto"""
        try:
            print("🚀 Iniciando creación de estructura del proyecto...")
            self.create_directories()
            print("📁 Directorios creados")
            
            self.create_requirements()
            print("📄 Archivo requirements.txt creado")
            
            self.create_project_files()
            print("✅ Archivos del proyecto creados")
            
            print("\n📁 Estructura del proyecto:")
            print("  src/")
            print("  ├── config.py")
            print("  ├── main.py")
            print("  ├── shared/")
            print("  │   ├── database.py")
            print("  │   └── exceptions.py")
            print("  └── features/")
            print("      ├── usuarios/")
            print("      └── productos/")
            
            print("\n📝 Siguientes pasos:")
            print("  1. Crear entorno virtual:")
            print("     python -m venv venv")
            print("  2. Activar entorno virtual:")
            print("     source venv/bin/activate  # Linux/Mac")
            print("     .\\venv\\Scripts\\activate  # Windows")
            print("  3. Instalar dependencias:")
            print("     pip install -r requirements.txt")
            print("  4. Ejecutar la aplicación:")
            print("     uvicorn src.main:app --reload")
            print("\n🌐 La API estará disponible en:")
            print("   http://localhost:8000")
            print("   http://localhost:8000/docs  # Documentación Swagger")
            
        except Exception as e:
            print(f"❌ Error durante la creación del proyecto: {str(e)}")
            sys.exit(1)

def main():
    """Función principal"""
    setup = ProjectSetup()
    setup.setup()

if __name__ == "__main__":
    main()