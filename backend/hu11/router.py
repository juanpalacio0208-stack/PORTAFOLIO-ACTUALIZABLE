
import sqlite3

from fastapi import APIRouter, HTTPException, status

from .models import UsuarioRegistro, UsuarioRespuesta
from .repository import crear_usuario

router = APIRouter(
    prefix="/api/auth",
    tags=["HU-11 Registro de usuarios"],
)


@router.post(
    "/registro",
    response_model=UsuarioRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def registrar_usuario(datos: UsuarioRegistro):
    try:
        usuario = crear_usuario(datos)
        return usuario

    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=409,
            detail="Este correo electrónico ya está registrado.",
        ) from exc

    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=500,
            detail="No fue posible completar el registro.",
        ) from exc
