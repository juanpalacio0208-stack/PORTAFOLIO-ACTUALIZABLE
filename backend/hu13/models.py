from typing import Literal

from pydantic import BaseModel, StrictBool


class UsuarioAdministracion(BaseModel):
    id: int
    nombre_completo: str
    correo: str
    activo: bool
    rol: str


class UsuarioActualizacionAdmin(BaseModel):
    activo: StrictBool | None = None
    rol: Literal["usuario", "administrador"] | None = None

