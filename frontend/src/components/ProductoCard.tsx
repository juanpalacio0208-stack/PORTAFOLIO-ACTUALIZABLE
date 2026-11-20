import type { Producto } from '../types/Producto'

interface Props {
  producto: Producto
  verDetalle: (producto: Producto) => void
}

function ProductoCard({ producto, verDetalle }: Props) {
  const precioFormateado = producto.precio.toLocaleString('es-CO', {
    style: 'currency', currency: 'COP', maximumFractionDigits: 0,
  })

  return (
    <article className="producto-card">
      <img src={producto.imagen} alt={producto.nombre} loading="lazy" />
      <div className="producto-contenido">
        <span className="producto-estado">{producto.disponible ? 'Disponible' : 'Agotado'}</span>
        <h3>{producto.nombre}</h3>
        <p>{producto.descripcion}</p>
        <strong className="producto-precio">{precioFormateado}</strong>
        <button type="button" className="boton-producto" onClick={() => verDetalle(producto)} aria-label={`Ver información de ${producto.nombre}`}>
          Ver producto
        </button>
      </div>
    </article>
  )
}

export default ProductoCard
