
import { useState } from 'react'
import PortafolioPage from './pages/PortafolioPage'
import ProductoDetallePage from './pages/ProductoDetallePage'
import RegistroPage from './pages/RegistroPage'
import type { Producto } from './types/Producto'
import './detalle-producto.css'

function App() {
  const [productoSeleccionado, setProductoSeleccionado] =
    useState<Producto | null>(null)

  const [mostrarRegistro, setMostrarRegistro] = useState(false)

  if (mostrarRegistro) {
    return (
      <RegistroPage
        volver={() => setMostrarRegistro(false)}
      />
    )
  }

  if (productoSeleccionado) {
    return (
      <ProductoDetallePage
        producto={productoSeleccionado}
        volver={() => setProductoSeleccionado(null)}
      />
    )
  }

  return (
    <PortafolioPage
      verDetalle={setProductoSeleccionado}
      abrirRegistro={() => setMostrarRegistro(true)}
    />
  )
}

export default App
