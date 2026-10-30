
import json
from pathlib import Path

from fastapi import HTTPException

ARCHIVO_PRODUCTOS = Path(__file__).resolve().parent.parent / "productos.json"


def obtener_producto(producto_id: int) -> dict:
    """Obtiene y valida un producto del catálogo del backend."""

    try:
        with ARCHIVO_PRODUCTOS.open("r", encoding="utf-8") as archivo:
            productos = json.load(archivo)
    except (OSError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=500,
            detail="No fue posible consultar el catálogo de productos.",
        ) from exc

    if not isinstance(productos, list):
        raise HTTPException(
            status_code=500,
            detail="El catálogo de productos no tiene un formato válido.",
        )

    for producto in productos:
        if producto.get("id") == producto_id:
            if not producto.get("disponible", False):
                raise HTTPException(
                    status_code=409,
                    detail="El producto no está disponible para solicitar.",
                )

            return producto

    raise HTTPException(
        status_code=404,
        detail="El producto seleccionado no existe.",
    )
