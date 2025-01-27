from sqlalchemy.orm import Session
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
