
from pydantic import BaseModel, EmailStr, Field


class CredencialesLogin(BaseModel):
    correo: EmailStr
    contrasena: str = Field(min_length=1)


class UsuarioAutenticado(BaseModel):
    id: int
    nombre_completo: str
    correo: EmailStr
    activo: bool


class RespuestaLogin(BaseModel):
    mensaje: str
    usuario: UsuarioAutenticado
