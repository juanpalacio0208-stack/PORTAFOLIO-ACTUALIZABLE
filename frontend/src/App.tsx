import { useState } from 'react'
import PortafolioPage from './pages/PortafolioPage'
import ProductoDetallePage from './pages/ProductoDetallePage'
import type { Producto } from './types/Producto'
import './detalle-producto.css'

function App() {
  const [productoSeleccionado, setProductoSeleccionado] = useState<Producto | null>(null)

  return productoSeleccionado ? (
    <ProductoDetallePage
      producto={productoSeleccionado}
      volver={() => setProductoSeleccionado(null)}
    />
  ) : (
    <PortafolioPage verDetalle={setProductoSeleccionado} />
  )
}

export default App
