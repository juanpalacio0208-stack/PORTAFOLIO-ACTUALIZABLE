"""Datos mayoristas definidos en JSON; contratos listos para migrar a la BD."""

from pydantic import BaseModel, ConfigDict, Field


class ProductoMayorista(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int = Field(gt=0)
    nombre: str = Field(min_length=1)
    descripcion: str = Field(min_length=1)
    categoria: str = Field(min_length=1)
    precio_mayorista: int = Field(ge=0, description="Precio por unidad en COP")
    cantidad_minima: int = Field(ge=1, description="Unidades mínimas por compra")
    condiciones_compra: str = Field(min_length=1)
    disponible: bool
    venta_mayorista: bool
