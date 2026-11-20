
import { useState } from 'react'
import type { Producto } from '../types/Producto'
import {
  crearSolicitud,
  type SolicitudProducto,
} from '../services/solicitudesApi'

interface Props {
  producto: Producto
  volver: () => void
  onSolicitudCreada: (solicitud: SolicitudProducto) => void
}

function ProductoDetallePage({
  producto,
  volver,
  onSolicitudCreada,
}: Props) {
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const precioFormateado = producto.precio.toLocaleString('es-CO', {
    style: 'currency',
    currency: 'COP',
    maximumFractionDigits: 0,
  })

  async function solicitarProducto() {
    if (cargando || !producto.disponible) return

    setCargando(true)
    setError(null)

    try {
      const nuevaSolicitud = await crearSolicitud(producto.id)
      onSolicitudCreada(nuevaSolicitud)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Ocurrió un error al solicitar el producto.'
      )
    } finally {
      setCargando(false)
    }
  }

  return (
    <>
      <header className="header">
        <div className="contenedor navegacion">
          <button
            className="detalle-logo"
            type="button"
            onClick={volver}
          >
            Portafolio
          </button>

          <nav>
            <button
              className="detalle-nav"
              type="button"
              onClick={volver}
            >
              Volver al catálogo
            </button>
          </nav>
        </div>
      </header>

      <main className="contenedor detalle-producto">
        <button
          type="button"
          className="boton-volver"
          onClick={volver}
        >
          ← Volver al catálogo
        </button>

        <div className="detalle-grid">
          <img
            src={producto.imagen}
            alt={producto.nombre}
            className="detalle-imagen"
          />

          <div className="detalle-informacion">
            <span className="producto-estado">
              {producto.disponible ? 'Disponible' : 'Agotado'}
            </span>

            <h1>{producto.nombre}</h1>
            <p>{producto.descripcion}</p>

            <strong className="detalle-precio">
              {precioFormateado}
            </strong>

            <h2>Información del producto</h2>

            <dl className="detalle-atributos">
              <dt>Nombre</dt>
              <dd>{producto.nombre}</dd>

              <dt>Descripción</dt>
              <dd>{producto.descripcion}</dd>

              <dt>Disponibilidad</dt>
              <dd>
                {producto.disponible
                  ? 'Disponible para solicitar'
                  : 'No disponible para solicitar'}
              </dd>
            </dl>

            <p className="detalle-aviso">
              {producto.disponible
                ? 'Puedes iniciar una solicitud para este producto.'
                : 'Este producto no se encuentra disponible actualmente.'}
            </p>

            <button
              type="button"
              className="boton-principal"
              onClick={() => void solicitarProducto()}
              disabled={!producto.disponible || cargando}
            >
              {cargando
                ? 'Registrando solicitud...'
                : 'Solicitar producto'}
            </button>

            {error && (
              <p role="alert" style={{ color: '#b91c1c' }}>
                {error}
              </p>
            )}
          </div>
        </div>
      </main>
    </>
  )
}

export default ProductoDetallePage