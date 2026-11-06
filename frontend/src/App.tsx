
import { useEffect, useState } from 'react'
import PortafolioPage from './pages/PortafolioPage'
import ProductoDetallePage from './pages/ProductoDetallePage'
import RegistroPage from './pages/RegistroPage'
import LoginPage from './pages/LoginPage'
import CuentaPage from './pages/CuentaPage'
import {
  consultarSesion,
  type UsuarioAutenticado,
} from './services/loginApi'
import type { Producto } from './types/Producto'
import './detalle-producto.css'

type Vista = 'portafolio' | 'registro' | 'login' | 'cuenta'

function App() {
  const [vista, setVista] = useState<Vista>('portafolio')
  const [productoSeleccionado, setProductoSeleccionado] =
    useState<Producto | null>(null)
  const [usuario, setUsuario] =
    useState<UsuarioAutenticado | null>(null)
  const [verificandoSesion, setVerificandoSesion] = useState(true)

  useEffect(() => {
    let activo = true

    consultarSesion()
      .then((datos) => {
        if (activo) setUsuario(datos)
      })
      .catch(() => {
        if (activo) setUsuario(null)
      })
      .finally(() => {
        if (activo) setVerificandoSesion(false)
      })

    return () => {
      activo = false
    }
  }, [])

  if (verificandoSesion) {
    return <main role="status">Verificando sesión...</main>
  }

  if (vista === 'registro') {
    return <RegistroPage volver={() => setVista('portafolio')} />
  }

  if (vista === 'login') {
    return (
      <LoginPage
        volver={() => setVista('portafolio')}
        onLogin={(datos) => {
          setUsuario(datos)
          setVista('cuenta')
        }}
      />
    )
  }

  if (vista === 'cuenta' && usuario) {
    return (
      <CuentaPage
        usuario={usuario}
        onLogout={() => {
          setUsuario(null)
          setVista('portafolio')
        }}
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
      abrirRegistro={() => setVista('registro')}
      abrirLogin={() => setVista(usuario ? 'cuenta' : 'login')}
    />
  )
}

export default App
