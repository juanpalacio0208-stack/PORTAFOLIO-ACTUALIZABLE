import type { Producto } from '../types/Producto'

interface ProductoCardProps {
  producto: Producto
}

function ProductoCard({ producto }: ProductoCardProps) {
  const precioFormateado = producto.precio.toLocaleString('es-CO', {
    style: 'currency',
    currency: 'COP',
    maximumFractionDigits: 0,
  })

  return (
    <article className="producto-card">
      <img
        src={producto.imagen}
        alt={producto.nombre}
        className="producto-imagen"
      />

      <div className="producto-contenido">
        <span className="producto-estado">
          Disponible
        </span>

        <h3>{producto.nombre}</h3>

        <p>{producto.descripcion}</p>

        <strong className="producto-precio">
          {precioFormateado}
        </strong>

        <button type="button" className="boton-producto">
          Ver producto
        </button>
      </div>
    </article>
  )
}

export default ProductoCard