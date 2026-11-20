import { useState } from 'react'
import type { FormEvent } from 'react'
import { restablecerContrasena } from '../services/recuperacionApi'
import '../recuperacion.css'

interface Props {
  token: string
  volver: () => void
}

export default function RestablecerContrasenaPage({ token, volver }: Props) {
  const [contrasena, setContrasena] = useState('')
  const [confirmacion, setConfirmacion] = useState('')
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState('')
  const [completado, setCompletado] = useState(false)

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setError('')
    if (contrasena.length < 8) {
      setError('La contraseña debe tener al menos 8 caracteres.')
      return
    }
    if (contrasena !== confirmacion) {
      setError('Las contraseñas no coinciden.')
      return
    }
    setCargando(true)
    try {
      await restablecerContrasena(token, contrasena)
      setCompletado(true)
      setContrasena('')
      setConfirmacion('')
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
        <h1>Crear nueva contraseña</h1>
        {completado ? (
          <>
            <div className="hu18-exito" role="status">
              Tu contraseña se actualizó correctamente. Ya puedes iniciar sesión.
            </div>
            <button className="hu18-principal" type="button" onClick={volver}>
              Ir a iniciar sesión
            </button>
          </>
        ) : (
          <form onSubmit={(evento) => void enviar(evento)}>
            <p>Elige una contraseña de al menos 8 caracteres.
              El enlace tiene una duración de 15 minutos y solo funciona una vez.</p>
            <label htmlFor="hu18-nueva">Nueva contraseña</label>
            <input id="hu18-nueva" type="password" autoComplete="new-password"
              minLength={8} maxLength={128} required value={contrasena}
              onChange={(evento) => setContrasena(evento.target.value)} />
            <label htmlFor="hu18-confirmar">Confirmar contraseña</label>
            <input id="hu18-confirmar" type="password" autoComplete="new-password"
              minLength={8} maxLength={128} required value={confirmacion}
              onChange={(evento) => setConfirmacion(evento.target.value)} />
            {error && <p className="hu18-error" role="alert">{error}</p>}
            <button className="hu18-principal" disabled={cargando} type="submit">
              {cargando ? 'Guardando...' : 'Actualizar contraseña'}
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
