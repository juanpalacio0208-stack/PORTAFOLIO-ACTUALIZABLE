import { useState } from 'react'
import type { FormEvent } from 'react'
import { solicitarRecuperacion } from '../services/recuperacionApi'
import '../recuperacion.css'

interface Props {
  volver: () => void
}

export default function RecuperarContrasenaPage({ volver }: Props) {
  const [correo, setCorreo] = useState('')
  const [cargando, setCargando] = useState(false)
  const [mensaje, setMensaje] = useState('')
  const [error, setError] = useState('')

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setError('')
    setMensaje('')
    if (!correo.trim()) {
      setError('Ingresa tu correo electrónico.')
      return
    }
    setCargando(true)
    try {
      const respuesta = await solicitarRecuperacion(correo.trim())
      setMensaje(respuesta)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ocurrió un error de conexión.')
    } finally {
      setCargando(false)
    }
  }

  return (
    <main className="hu18-fondo">
      <section className="hu18-tarjeta">
        <span className="hu18-etiqueta">SEGURIDAD DE LA CUENTA</span>
        <h1>Recuperar contraseña</h1>
        <p>Ingresa el correo con el que creaste tu cuenta. Si está registrado,
          recibirás un enlace temporal para cambiar tu contraseña.</p>
        {mensaje ? (
          <div className="hu18-exito" role="status">{mensaje}</div>
        ) : (
          <form onSubmit={(evento) => void enviar(evento)}>
            <label htmlFor="hu18-correo">Correo electrónico</label>
            <input
              id="hu18-correo" type="email" required autoComplete="email"
              placeholder="correo@ejemplo.com"
              value={correo} onChange={(evento) => setCorreo(evento.target.value)}
            />
            {error && <p className="hu18-error" role="alert">{error}</p>}
            <button className="hu18-principal" type="submit" disabled={cargando}>
              {cargando ? 'Procesando...' : 'Solicitar recuperación'}
            </button>
          </form>
        )}
        <button className="hu18-volver" type="button" onClick={volver}>
          ← Volver al inicio de sesión
        </button>
      </section>
    </main>
  )
}
