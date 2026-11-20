import { useState, type FormEvent } from 'react'
import { actualizarPerfil, cerrarSesion, type UsuarioAutenticado } from '../services/loginApi'
import '../login.css'

interface Props {
  usuario: UsuarioAutenticado
  onLogout: () => void
  onUsuarioActualizado: (usuario: UsuarioAutenticado) => void
}

function CuentaPage({ usuario, onLogout, onUsuarioActualizado }: Props) {
  const [error, setError] = useState('')
  const [procesando, setProcesando] = useState(false)
  const [editando, setEditando] = useState(false)
  const [nombre, setNombre] = useState(usuario.nombre_completo)
  const [correo, setCorreo] = useState(usuario.correo)
  const [contrasena, setContrasena] = useState('')
  const [confirmacion, setConfirmacion] = useState('')

  async function guardarPerfil(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setError('')
    if (contrasena && contrasena !== confirmacion) {
      setError('Las contraseñas no coinciden.')
      return
    }
    setProcesando(true)
    try {
      const actualizado = await actualizarPerfil({ nombre_completo: nombre, correo, ...(contrasena ? { contrasena } : {}) })
      onUsuarioActualizado(actualizado)
      setContrasena('')
      setConfirmacion('')
      setEditando(false)
    } catch (causa) {
      setError(causa instanceof Error ? causa.message : 'No fue posible actualizar el perfil.')
    } finally {
      setProcesando(false)
    }
  }

  async function manejarSalida() {
    setError('')
    setProcesando(true)
    try { await cerrarSesion(); onLogout() }
    catch { setError('No fue posible cerrar sesión.') }
    finally { setProcesando(false) }
  }

  return <main className="login-contenedor"><section className="login-tarjeta">
    <h1>Mi cuenta</h1>
    <p>Bienvenido, <strong>{usuario.nombre_completo}</strong>.</p>
    <p><strong>Correo:</strong> {usuario.correo}</p>
    <p>Has iniciado sesión correctamente.</p>
    {editando ? <form onSubmit={(evento) => void guardarPerfil(evento)}>
      <label htmlFor="perfil-nombre">Nombre completo</label>
      <input id="perfil-nombre" required minLength={3} maxLength={100} value={nombre} onChange={(evento) => setNombre(evento.target.value)} />
      <label htmlFor="perfil-correo">Correo electrónico</label>
      <input id="perfil-correo" type="email" required value={correo} onChange={(evento) => setCorreo(evento.target.value)} />
      <label htmlFor="perfil-contrasena">Nueva contraseña (opcional)</label>
      <input id="perfil-contrasena" type="password" minLength={8} autoComplete="new-password" value={contrasena} onChange={(evento) => setContrasena(evento.target.value)} />
      {contrasena && <><label htmlFor="perfil-confirmacion">Confirmar contraseña</label><input id="perfil-confirmacion" type="password" required autoComplete="new-password" value={confirmacion} onChange={(evento) => setConfirmacion(evento.target.value)} /></>}
      <button type="submit" disabled={procesando}>{procesando ? 'Guardando…' : 'Guardar cambios'}</button>
      <button type="button" disabled={procesando} onClick={() => setEditando(false)}>Cancelar</button>
    </form> : <button type="button" className="hu14-abrir" onClick={() => setEditando(true)}>Actualizar perfil</button>}
    {error && <p role="alert">{error}</p>}
    <button type="button" disabled={procesando} onClick={() => void manejarSalida()}>{procesando ? 'Procesando…' : 'Cerrar sesión'}</button>
  </section></main>
}

export default CuentaPage
