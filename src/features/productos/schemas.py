from pydantic import BaseModel, Field
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
