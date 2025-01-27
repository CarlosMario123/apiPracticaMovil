from sqlalchemy.orm import Session
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
