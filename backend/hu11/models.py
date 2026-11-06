
from pydantic import BaseModel, EmailStr, Field, field_validator


class UsuarioRegistro(BaseModel):
    nombre_completo: str = Field(min_length=3, max_length=100)
    correo: EmailStr
    contrasena: str = Field(min_length=8, max_length=128)

    @field_validator("nombre_completo", mode="before")
    @classmethod
    def limpiar_nombre(cls, valor):
        if isinstance(valor, str):
            return valor.strip()
        return valor

    @field_validator("nombre_completo")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        if not valor:
            raise ValueError("El nombre completo es obligatorio")
        return valor

    @field_validator("contrasena")
    @classmethod
    def validar_contrasena(cls, valor: str) -> str:
        if not any(letra.isalpha() for letra in valor):
            raise ValueError(
                "La contraseña debe contener al menos una letra"
            )

        if not any(caracter.isdigit() for caracter in valor):
            raise ValueError(
                "La contraseña debe contener al menos un número"
            )

        return valor


class UsuarioRespuesta(BaseModel):
    id: int
    nombre_completo: str
    correo: EmailStr
    activo: bool
