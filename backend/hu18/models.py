"""Modelos de la HU-18: recuperación de contraseña."""

from pydantic import BaseModel, EmailStr, Field


class SolicitudRecuperacion(BaseModel):
    correo: EmailStr


class RestablecimientoContrasena(BaseModel):
    token: str = Field(min_length=20, max_length=200)
    nueva_contrasena: str = Field(min_length=8, max_length=128)


class RespuestaMensaje(BaseModel):
    mensaje: str
