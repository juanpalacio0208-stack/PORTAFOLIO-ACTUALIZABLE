"""HU-06 — Consultar productos como administradora.

Aplicación local de demostración (SIN autenticación). No exponer a internet
hasta implementar control de acceso para el rol administrador.
"""

import json
from html import escape
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

app = FastAPI(title="Importaciones Euroamericanas — HU-06", version="0.1.0")
ARCHIVO_PRODUCTOS = Path(__file__).resolve().parent / "productos.json"
app.mount("/static", StaticFiles(directory=Path(__file__).resolve().parent / "static"), name="static")


class Producto(BaseModel):
    id: int
    nombre: str
    descripcion: str
    categoria: str
    precio: float = Field(ge=0)
    disponible: bool


def cargar_productos() -> list[Producto]:
    """Lee JSON de disco cada vez, para reflejar los cambios actuales.

    Más adelante, esta función puede sustituirse por consultas a la BD,
    conservando las rutas de la API.
    """
    try:
        with ARCHIVO_PRODUCTOS.open("r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
        if not isinstance(datos, list):
            raise ValueError("El archivo debe contener una lista de productos.")
        return [Producto.model_validate(item) for item in datos]
    except (OSError, ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=500,
            detail="No fue posible leer los productos almacenados.",
        ) from exc


@app.get("/")
def inicio():
    return {"mensaje": "API de Portafolio Actualizable funcionando", "hu": "HU-06"}


@app.get("/api/admin/productos", response_model=list[Producto])
def consultar_productos():
    """Incluye todos los productos, tanto disponibles como agotados."""
    return cargar_productos()


@app.get("/api/admin/productos/{producto_id}", response_model=Producto)
def consultar_producto(producto_id: int):
    for producto in cargar_productos():
        if producto.id == producto_id:
            return producto
    raise HTTPException(status_code=404, detail="Producto no encontrado")


@app.get("/admin/productos", response_class=HTMLResponse)
def vista_productos():
    """Vista de consulta, no de creación o edición (pertenecen a otras HU)."""
    productos = cargar_productos()
    filas = []
    for p in productos:
        precio = f"$ {p.precio:,.0f}".replace(",", ".")
        estado = "Disponible" if p.disponible else "Agotado"
        clase_estado = "ok" if p.disponible else "agotado"
        filas.append(
            f'<tr><td>{p.id}</td>'
            f'<td><strong>{escape(p.nombre)}</strong><small>{escape(p.descripcion)}</small></td>'
            f'<td>{escape(p.categoria)}</td>'
            f'<td class="precio">{precio}</td>'
            f'<td><span class="estado {clase_estado}">{estado}</span></td></tr>'
        )

    filas_html = "".join(filas) or '<tr><td colspan="5" class="vacio">No hay productos registrados.</td></tr>'

    return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>HU-06 | Administración de productos</title>
  <style>
    :root {{ font-family: system-ui, Segoe UI, Arial, sans-serif; color: #222; background: #f7f7f5; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; }}
    header {{ background: #141414; color: white; padding: 26px 5%; }}
    header strong {{ color: #ecc356; letter-spacing: .08em; font-size: 1.05rem; }}
    .marca {{display: flex;align-items: center;gap: 14px;}}
    .marca img {{width: 64px;height: 64px;object-fit: cover;border-radius: 50%;}}
    header p {{ margin: 4px 0 0; color: #bdbdbd; font-size: .8rem; letter-spacing: .15em; }}
    main {{ max-width: 1120px; padding: 36px 22px; margin: auto; }}
    h1 {{ margin: 0 0 4px; font-size: clamp(1.5rem, 4vw, 2rem); }}
    .sub {{ color: #656565; margin: 0 0 24px; }}
    .resumen {{ display: inline-flex; gap: 12px; padding: 16px 20px; background: #fff4d2; border-radius: 12px; margin-bottom: 24px; }}
    .resumen b {{ color: #946f0b; }}
    .tabla {{ overflow-x: auto; border-radius: 14px; background: white; box-shadow: 0 5px 24px #0001; }}
    table {{ width: 100%; border-collapse: collapse; min-width: 730px; }}
    th {{ color: #fff; text-align: left; background: #222; font-weight: 600; padding: 15px; }}
    td {{ padding: 15px; border-bottom: 1px solid #ececec; vertical-align: middle; }}
    tr:last-child td {{ border-bottom: 0; }}
    td small {{ display: block; margin-top: 4px; color: #6b6b6b; }}
    .precio {{ font-weight: 700; color: #936b00; white-space: nowrap; }}
    .estado {{ display: inline-block; border-radius: 100px; padding: 7px 12px; font-size: .82rem; font-weight: 600; }}
    .estado.ok {{ background: #e2f8e7; color: #187536; }}
    .estado.agotado {{ background: #f9e6e3; color: #b63c2c; }}
    .vacio {{ text-align: center; color: #777; padding: 38px; }}
    .nota {{ margin-top: 24px; color: #777; font-size: .88rem; }}
    a {{ color: #775600; }}
  </style>
</head>
<body>
<header><div class="marca"><img src="/static/logo.png" alt="Logo de Importaciones Euroamericanas"><div><strong>IMPORTACIONES EUROAMERICANAS</strong><p>PANEL DE ADMINISTRACIÓN · DEMOSTRACIÓN LOCAL</p></div></div></header>
<main>
  <h1>HU-06 — Consultar productos</h1>
  <p class="sub">Visualiza los productos registrados y su información actual.</p>
  <div class="resumen">Productos registrados: <b>{len(productos)}</b></div>
  <div class="tabla"><table>
    <thead><tr><th>ID</th><th>Producto</th><th>Categoría</th><th>Precio</th><th>Disponibilidad</th></tr></thead>
    <tbody>{filas_html}</tbody>
  </table></div>
  <p class="nota">Datos de prueba leídos desde <code>productos.json</code>. Esta versión todavía no tiene login ni base de datos.
    Puedes consultar también <a href="/docs">la documentación de la API</a>.</p>
</main>
</body>
</html>"""
