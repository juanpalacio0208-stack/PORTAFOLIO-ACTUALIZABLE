"""Rutas HU-17 reutilizables en FastAPI independiente o en el backend común."""

from html import escape
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, FileResponse

from . import repository
from .models import ProductoMayorista

router = APIRouter(tags=["HU-17 Catálogo mayorista"])
_STATIC = Path(__file__).resolve().parent / "static"


def pesos(valor: int) -> str:
    return "$ " + f"{valor:,}".replace(",", ".")


@router.get("/api/mayoristas/productos", response_model=list[ProductoMayorista])
def listar_catalogo():
    """Excluye los agotados y los productos no habilitados para venta al por mayor."""
    return repository.listar_disponibles()


@router.get("/api/mayoristas/productos/{producto_id}", response_model=ProductoMayorista)
def ver_producto_mayorista(producto_id: int):
    for producto in repository.listar_disponibles():
        if producto.id == producto_id:
            return producto
    raise HTTPException(status_code=404, detail="Producto mayorista no disponible")


@router.get("/mayoristas/estilos.css", include_in_schema=False)
def estilos():
    return FileResponse(_STATIC / "estilos.css", media_type="text/css")


@router.get("/mayoristas/logo.png", include_in_schema=False)
def logo():
    return FileResponse(_STATIC / "logo.png", media_type="image/png")


@router.get("/mayoristas", response_class=HTMLResponse)
def catalogo_web():
    """Vista pública, accesible al cliente mayorista sin login en esta HU."""
    productos = repository.listar_disponibles()
    tarjetas = []
    iconos = {"Cuidado personal": "✦", "Belleza": "♥", "Perfumes": "✧", "Accesorios": "◆"}

    for p in productos:
        nombre = escape(p.nombre)
        descripcion = escape(p.descripcion)
        categoria = escape(p.categoria)
        condiciones = escape(p.condiciones_compra)
        icono = iconos.get(p.categoria, "✦")
        tarjetas.append(f"""
        <article class="producto">
          <div class="ilustracion" aria-hidden="true"><span class="motivo">{icono}</span></div>
          <div class="detalle">
            <span class="categoria">{categoria}</span>
            <h3>{nombre}</h3>
            <p class="descripcion">{descripcion}</p>
            <p class="precio">{pesos(p.precio_mayorista)} <small>/unidad</small></p>
            <div class="minimo">Pedido mínimo: <strong>{p.cantidad_minima} unidades</strong></div>
            <details><summary>Ver condiciones de compra</summary><p>{condiciones}</p></details>
          </div>
        </article>""")

    resultado = "".join(tarjetas) or (
        '<div class="vacio" role="status">'
        '<strong>No hay productos mayoristas disponibles actualmente.</strong>'
        '<p>Vuelve a consultar el catálogo más adelante.</p></div>'
    )
    return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Catálogo de compras al por mayor, precios y condiciones de volumen">
  <title>Catálogo mayorista | Importaciones Euroamericanas</title>
  <link rel="stylesheet" href="/mayoristas/estilos.css">
</head>
<body>
<header class="barra">
  <div class="contenedor cabecera">
    <div class="marca"><img src="/mayoristas/logo.png" alt="Logo Importaciones Euroamericanas"><span>IMPORTACIONES <em>EUROAMERICANAS</em></span></div>
    <nav aria-label="Principal"><a href="#catalogo">Catálogo mayorista</a></nav>
  </div>
</header>
<main>
  <section class="hero">
    <div class="contenedor">
      <p class="antetitulo">VENTAS POR VOLUMEN · HU-17</p>
      <h1>Catálogo <span>mayorista</span></h1>
      <p class="introduccion">Consulta los productos habilitados para compras al por mayor, el precio por unidad y las condiciones mínimas registradas para cada referencia.</p>
      <a class="boton" href="#catalogo">Explorar catálogo <span aria-hidden="true">→</span></a>
    </div>
  </section>
  <section id="catalogo" class="contenedor seccion" aria-labelledby="titulo-catalogo">
    <div class="encabezado-seccion"><div><span class="etiqueta">OFERTA MAYORISTA</span><h2 id="titulo-catalogo">Productos disponibles</h2><p>Precios de ejemplo en pesos colombianos (COP), por unidad.</p></div><div class="contador">{len(productos)} referencias</div></div>
    <div class="grilla">{resultado}</div>
  </section>
</main>
<footer><div class="contenedor pie"><span>IMPORTACIONES EUROAMERICANAS</span><p>Prototipo académico · Datos y condiciones de ejemplo, sujetos a validación por Laura.</p></div></footer>
</body>
</html>"""
