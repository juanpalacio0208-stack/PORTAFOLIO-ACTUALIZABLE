from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class PerfilActualizacion(BaseModel):
    nombre_completo: str | None = Field(default=None, min_length=3, max_length=100)
    correo: EmailStr | None = None
    contrasena: str | None = Field(default=None, min_length=8, max_length=128)

    @field_validator("nombre_completo", mode="before")
    @classmethod
    def limpiar_nombre(cls, valor):
        return valor.strip() if isinstance(valor, str) else valor

    @field_validator("nombre_completo")
    @classmethod
    def validar_nombre(cls, valor):
        if valor is not None and not valor:
            raise ValueError("El nombre completo es obligatorio")
        return valor

    @field_validator("contrasena")
    @classmethod
    def validar_contrasena(cls, valor):
        if valor is not None and (
            not any(letra.isalpha() for letra in valor)
            or not any(caracter.isdigit() for caracter in valor)
        ):
            raise ValueError("La contraseña debe contener letras y números")
        return valor

    @model_validator(mode="after")
    def validar_cambios(self):
        if not self.model_fields_set or all(
            getattr(self, campo) is None for campo in self.model_fields_set
        ):
            raise ValueError("Indica al menos un dato para actualizar")
        return self
