from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from src.shared.database import get_db
from . import schemas, service
from typing import List

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

@router.post("/", response_model=schemas.Usuario, status_code=status.HTTP_201_CREATED)
def create_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    usuario_service = service.UsuarioService(db)
    return usuario_service.create(usuario)

@router.get("/{usuario_email}", response_model=schemas.Usuario)
def get_usuario(usuario_email: str, db: Session = Depends(get_db)):
    usuario_service = service.UsuarioService(db)
    return usuario_service.get_by_email(usuario_email)
