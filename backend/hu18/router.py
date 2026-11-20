"""Rutas de recuperación, compatibles con /api/auth de HU-12."""

from fastapi import APIRouter

from .models import RespuestaMensaje, RestablecimientoContrasena, SolicitudRecuperacion
from .service import restablecer_contrasena, solicitar_recuperacion

router = APIRouter(prefix="/api/auth", tags=["HU-18 Recuperar contraseña"])


@router.post("/recuperar", response_model=RespuestaMensaje)
def recuperar(datos: SolicitudRecuperacion):
    return {"mensaje": solicitar_recuperacion(str(datos.correo))}


@router.post("/restablecer", response_model=RespuestaMensaje)
def restablecer(datos: RestablecimientoContrasena):
    restablecer_contrasena(datos.token, datos.nueva_contrasena)
    return {"mensaje": "Contraseña actualizada. Ya puedes iniciar sesión."}
