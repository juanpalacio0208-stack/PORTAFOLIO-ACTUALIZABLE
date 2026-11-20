
import { useState } from 'react'
import PortafolioPage from './pages/PortafolioPage'
import ProductoDetallePage from './pages/ProductoDetallePage'
import ContactoCompradorPage from './pages/ContactoCompradorPage'
import type { Producto } from './types/Producto'
import type { SolicitudProducto } from './services/solicitudesApi'
import './detalle-producto.css'

function App() {
  const [productoSeleccionado, setProductoSeleccionado] =
    useState<Producto | null>(null)

  const [solicitudActual, setSolicitudActual] =
    useState<SolicitudProducto | null>(null)

  function volverCatalogo() {
    setSolicitudActual(null)
    setProductoSeleccionado(null)
  }

  if (productoSeleccionado && solicitudActual) {
    return (
      <ContactoCompradorPage
        solicitudId={solicitudActual.id}
        productoNombre={solicitudActual.producto_nombre}
        volver={() => setSolicitudActual(null)}
      />
    )
  }

  if (productoSeleccionado) {
    return (
      <ProductoDetallePage
        key={productoSeleccionado.id}
        producto={productoSeleccionado}
        volver={volverCatalogo}
        onSolicitudCreada={setSolicitudActual}
      />
    )
  }

  return <PortafolioPage verDetalle={setProductoSeleccionado} />
}

export default App
