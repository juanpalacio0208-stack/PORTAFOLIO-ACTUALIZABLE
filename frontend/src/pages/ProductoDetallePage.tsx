import type { Producto } from '../types/Producto'

interface Props {
  producto: Producto
  volver: () => void
}

function ProductoDetallePage({ producto, volver }: Props) {
  const precioFormateado = producto.precio.toLocaleString('es-CO', {
    style: 'currency', currency: 'COP', maximumFractionDigits: 0,
  })

  return (
    <>
      <header className="header">
        <div className="contenedor navegacion">
          <button className="detalle-logo" type="button" onClick={volver}>Portafolio</button>
          <nav><button className="detalle-nav" type="button" onClick={volver}>Volver al catálogo</button></nav>
        </div>
      </header>
      <main className="contenedor detalle-producto">
        <button type="button" className="boton-volver" onClick={volver}>← Volver al catálogo</button>
        <div className="detalle-grid">
          <img src={producto.imagen} alt={producto.nombre} className="detalle-imagen" />
          <div className="detalle-informacion">
            <span className="producto-estado">{producto.disponible ? 'Disponible' : 'Agotado'}</span>
            <h1>{producto.nombre}</h1>
            <p>{producto.descripcion}</p>
            <strong className="detalle-precio">{precioFormateado}</strong>
            <h2>Información del producto</h2>
            <dl className="detalle-atributos">
              <dt>Nombre</dt><dd>{producto.nombre}</dd>
              <dt>Descripción</dt><dd>{producto.descripcion}</dd>
              <dt>Disponibilidad</dt><dd>{producto.disponible ? 'Disponible para solicitar' : 'No disponible para solicitar'}</dd>
            </dl>
            <p className="detalle-aviso">{producto.disponible
              ? 'Este producto está disponible. La solicitud o compra se habilitará en una próxima funcionalidad.'
              : 'Este producto no se encuentra disponible actualmente.'}</p>
          </div>
        </div>
      </main>
    </>
  )
}

export default ProductoDetallePage
