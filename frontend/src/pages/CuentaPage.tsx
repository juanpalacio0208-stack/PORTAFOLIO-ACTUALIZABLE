import { useState } from 'react'
import { cerrarSesion, type UsuarioAutenticado } from '../services/loginApi'
import '../login.css'

interface Props {
  usuario: UsuarioAutenticado
  onLogout: () => void
  onAdministrarUsuarios: () => void
}

function CuentaPage({ usuario, onLogout, onAdministrarUsuarios }: Props) {
  const [error, setError] = useState('')
  const [cerrando, setCerrando] = useState(false)
  async function manejarSalida() {
    setError('')
    setCerrando(true)
    try { await cerrarSesion(); onLogout() }
    catch { setError('No fue posible cerrar sesión.') }
    finally { setCerrando(false) }
  }
  return <main className="login-contenedor hu13-contenedor"><section className="login-tarjeta">
    <h1>Mi cuenta</h1>
    <p>Bienvenido, <strong>{usuario.nombre_completo}</strong>.</p>
    <p><strong>Correo:</strong> {usuario.correo}</p>
    {usuario.rol === 'administrador' && <button type="button" className="hu14-abrir" onClick={onAdministrarUsuarios}>Administrar usuarios</button>}
    {error && <p role="alert">{error}</p>}
    <button type="button" disabled={cerrando} onClick={() => void manejarSalida()}>{cerrando ? 'Cerrando sesión…' : 'Cerrar sesión'}</button>
  </section></main>
}

export default CuentaPage
