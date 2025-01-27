from fastapi import APIRouter, Depends, status
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
