
import { useState } from 'react'
import type { FormEvent } from 'react'
import {
  iniciarSesion,
  type UsuarioAutenticado,
} from '../services/loginApi'
import '../login.css'

interface Props {
  volver: () => void
  onLogin: (usuario: UsuarioAutenticado) => void
}

function LoginPage({ volver, onLogin }: Props) {
  const [correo, setCorreo] = useState('')
  const [contrasena, setContrasena] = useState('')
  const [error, setError] = useState('')
  const [cargando, setCargando] = useState(false)

  async function manejarEnvio(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setError('')

    if (!correo.trim() || !contrasena) {
      setError('Debes ingresar el correo y la contraseña.')
      return
    }

    setCargando(true)

    try {
      const usuario = await iniciarSesion(correo.trim(), contrasena)
      onLogin(usuario)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Ocurrió un error al iniciar sesión.'
      )
    } finally {
      setCargando(false)
    }
  }

  return (
    <main className="login-contenedor">
      <section className="login-tarjeta">
        <button type="button" className="login-volver" onClick={volver}>
          ← Volver al portafolio
        </button>

        <h1>Iniciar sesión</h1>
        <p>Ingresa tus credenciales para acceder a tu cuenta.</p>

        <form onSubmit={(evento) => void manejarEnvio(evento)} noValidate>
          <label htmlFor="login-correo">Correo electrónico *</label>
          <input
            id="login-correo"
            type="email"
            value={correo}
            autoComplete="email"
            onChange={(evento) => setCorreo(evento.target.value)}
            required
          />

          <label htmlFor="login-contrasena">Contraseña *</label>
          <input
            id="login-contrasena"
            type="password"
            value={contrasena}
            autoComplete="current-password"
            onChange={(evento) => setContrasena(evento.target.value)}
            required
          />

          {error && <p role="alert">{error}</p>}

          <button type="submit" disabled={cargando}>
            {cargando ? 'Ingresando...' : 'Iniciar sesión'}
          </button>
        </form>
      </section>
    </main>
  )
}

export default LoginPage
