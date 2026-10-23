from pydantic import BaseModel, Field, field_validator

class DatosProducto(BaseModel):
    nombre: str = Field(min_length=1,max_length=120)
    descripcion: str = Field(min_length=1,max_length=600)
    categoria: str = Field(min_length=1,max_length=100)
    precio: float = Field(gt=0,le=999999999)
    imagen_url: str | None = Field(default=None,max_length=1000)

    @field_validator('nombre','descripcion','categoria')
    @classmethod
    def no_vacio(cls,v):
        v=v.strip()
        if not v: raise ValueError('No puede estar en blanco')
        return v

    @field_validator('imagen_url')
    @classmethod
    def imagen_valida(cls,v):
        if v is None: return None
        v=v.strip()
        if v and not v.startswith(('http://','https://')):
            raise ValueError('La URL debe empezar por http:// o https://')
        return v or None

class ProductoNuevo(DatosProducto):
    disponible: bool

class Disponibilidad(BaseModel):
    disponible: bool
