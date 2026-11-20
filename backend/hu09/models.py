
from pydantic import BaseModel, EmailStr, Field, field_validator


class ContactoComprador(BaseModel):
    nombre_completo: str = Field(min_length=3, max_length=100)
    telefono: str = Field(min_length=10, max_length=15)
    correo: EmailStr | None = None

    @field_validator("nombre_completo", "telefono", mode="before")
    @classmethod
    def limpiar_campos(cls, valor):
        if isinstance(valor, str):
            return valor.strip()
        return valor

    @field_validator("nombre_completo")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        if not valor:
            raise ValueError("El nombre completo es obligatorio")
        return valor

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, valor: str) -> str:
        numero = valor.removeprefix("+")
        if not numero.isdigit():
            raise ValueError(
                "El teléfono solo puede contener números y un + inicial"
            )
        return valor
