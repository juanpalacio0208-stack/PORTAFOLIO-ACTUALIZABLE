"""Acceso a datos intercambiable: sustituir cargar_productos() por consulta a BD."""

import json
from pathlib import Path

from fastapi import HTTPException
from pydantic import ValidationError

from .models import ProductoMayorista

ARCHIVO_PRODUCTOS = Path(__file__).resolve().parent / "catalogo_mayorista.json"


def cargar_productos() -> list[ProductoMayorista]:
    """Siempre lee el JSON actual, sin mantener una copia desactualizada en memoria."""
    try:
        with ARCHIVO_PRODUCTOS.open("r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
        if not isinstance(datos, list):
            raise ValueError("El JSON debe contener una lista")
        return [ProductoMayorista.model_validate(producto) for producto in datos]
    except (OSError, ValueError, TypeError, ValidationError) as exc:
        raise HTTPException(
            status_code=500,
            detail="No se pudo consultar el catálogo mayorista.",
        ) from exc


def listar_disponibles() -> list[ProductoMayorista]:
    """Mostrar solamente referencias habilitadas y disponibles para mayoristas."""
    return [
        producto
        for producto in cargar_productos()
        if producto.disponible and producto.venta_mayorista
    ]
