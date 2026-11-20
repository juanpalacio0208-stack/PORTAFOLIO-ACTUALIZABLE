

import { useEffect, useState } from 'react'
import PortafolioPage from './pages/PortafolioPage'
import ProductoDetallePage from './pages/ProductoDetallePage'
import ContactoCompradorPage from './pages/ContactoCompradorPage'
import RegistroPage from './pages/RegistroPage'
import LoginPage from './pages/LoginPage'
import RecuperarContrasenaPage from './pages/RecuperarContrasenaPage'
import RestablecerContrasenaPage from './pages/RestablecerContrasenaPage'
import CuentaPage from './pages/CuentaPage'
import ConsentimientoNotificacionesPage from './pages/ConsentimientoNotificacionesPage'

import {
  consultarSesion,
  type UsuarioAutenticado,
} from './services/loginApi'

import type { Producto } from './types/Producto'
import type { SolicitudProducto } from './services/solicitudesApi'

import './detalle-producto.css'

type Vista = 'portafolio' | 'registro' | 'login' | 'cuenta' | 'recuperar' | 'restablecer' | 'notificaciones'

function App() {
  const [tokenRestablecimiento] = useState(() =>
    new URLSearchParams(window.location.hash.slice(1)).get('recuperar_token') ?? ''
  )
  const [vista, setVista] = useState<Vista>(
    tokenRestablecimiento ? 'restablecer' : 'portafolio'
  )

  const [productoSeleccionado, setProductoSeleccionado] =
    useState<Producto | null>(null)

  const [solicitudActual, setSolicitudActual] =
    useState<SolicitudProducto | null>(null)

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

  function volverCatalogo() {
    setSolicitudActual(null)
    setProductoSeleccionado(null)
    setVista('portafolio')
  }

  if (verificandoSesion) {
    return <main role="status">Verificando sesión...</main>
  }

  if (vista === 'registro') {
    return (
      <RegistroPage
        volver={() => setVista('portafolio')}
      />
    )
  }

  if (vista === 'recuperar') {
    return <RecuperarContrasenaPage volver={() => setVista('login')} />
  }

  if (vista === 'restablecer') {
    return (
      <RestablecerContrasenaPage
        token={tokenRestablecimiento}
        volver={() => {
          window.history.replaceState({}, '', window.location.pathname + window.location.search)
          setVista('login')
        }}
      />
    )
  }

  if (vista === 'login') {
    return (
      <LoginPage
        volver={() => setVista('portafolio')}
        abrirRecuperacion={() => setVista('recuperar')}
        onLogin={(datos) => {
          setUsuario(datos)
          setVista('cuenta')
        }}
      />
    )
  }

  if (vista === 'notificaciones' && usuario) {
    return <ConsentimientoNotificacionesPage volver={() => setVista('cuenta')} />
  }

  if (vista === 'cuenta' && usuario) {
    return (
      <CuentaPage
        usuario={usuario}
        onVolver={() => setVista('portafolio')}
        onPreferencias={() => setVista('notificaciones')}
        onLogout={() => {
          setUsuario(null)
          setVista('portafolio')
        }}
      />
    )
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

  return (
    <PortafolioPage
      verDetalle={setProductoSeleccionado}
      abrirRegistro={() => setVista('registro')}
      abrirLogin={() => setVista(usuario ? 'cuenta' : 'login')}
    />
  )
}

export default App
