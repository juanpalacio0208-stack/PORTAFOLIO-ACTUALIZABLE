
import { useState } from 'react'
import type { FormEvent } from 'react'
import {
  registrarUsuario,
  type UsuarioRegistrado,
} from '../services/registroApi'
import '../registro.css'

interface Props {
  volver: () => void
}

function RegistroPage({ volver }: Props) {
  const [nombre, setNombre] = useState('')
  const [correo, setCorreo] = useState('')
  const [contrasena, setContrasena] = useState('')
  const [errores, setErrores] = useState<Record<string, string>>({})
  const [errorGeneral, setErrorGeneral] = useState('')
  const [cargando, setCargando] = useState(false)
  const [usuario, setUsuario] = useState<UsuarioRegistrado | null>(null)

  function validar() {
    const nuevosErrores: Record<string, string> = {}

    if (nombre.trim().length < 3) {
      nuevosErrores.nombre = 'Ingresa un nombre de al menos 3 caracteres.'
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correo.trim())) {
      nuevosErrores.correo = 'Ingresa un correo electrónico válido.'
    }

    if (contrasena.length < 8 || contrasena.length > 128) {
      nuevosErrores.contrasena = 'La contraseña debe tener entre 8 y 128 caracteres.'
    } else if (!/[A-Za-zÀ-ÿ]/.test(contrasena) || !/\d/.test(contrasena)) {
      nuevosErrores.contrasena = 'Incluye al menos una letra y un número.'
    }

    return nuevosErrores
  }

  async function manejarRegistro(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    const nuevosErrores = validar()
    setErrores(nuevosErrores)
    setErrorGeneral('')

    if (Object.keys(nuevosErrores).length > 0) return

    setCargando(true)

    try {
      const registrado = await registrarUsuario({
        nombre_completo: nombre.trim(),
        correo: correo.trim(),
        contrasena,
      })
      setUsuario(registrado)
      setContrasena('')
    } catch (error) {
      setErrorGeneral(
        error instanceof Error ? error.message : 'Ocurrió un error.'
      )
    } finally {
      setCargando(false)
    }
  }

  if (usuario) {
    return (
      <main className="registro-contenedor">
        <section className="registro-tarjeta" role="status">
          <h1>¡Registro exitoso!</h1>
          <p>Bienvenido, <strong>{usuario.nombre_completo}</strong>.</p>
          <p>Tu cuenta fue creada correctamente.</p>
          <p>Podrás iniciar sesión cuando esté habilitada HU-12.</p>
          <button type="button" onClick={volver}>
            Volver al portafolio
          </button>
        </section>
      </main>
    )
  }

  return (
    <main className="registro-contenedor">
      <section className="registro-tarjeta">
        <button type="button" onClick={volver} className="registro-volver">
          ← Volver al portafolio
        </button>

        <h1>Crear cuenta</h1>
        <p>Regístrate para acceder a las funcionalidades de compradores.</p>

        <form onSubmit={(evento) => void manejarRegistro(evento)} noValidate>
          <label htmlFor="nombre">Nombre completo *</label>
          <input
            id="nombre"
            value={nombre}
            autoComplete="name"
            onChange={(e) => setNombre(e.target.value)}
            aria-invalid={Boolean(errores.nombre)}
          />
          {errores.nombre && <p role="alert">{errores.nombre}</p>}

          <label htmlFor="correo">Correo electrónico *</label>
          <input
            id="correo"
            type="email"
            value={correo}
            autoComplete="email"
            onChange={(e) => setCorreo(e.target.value)}
            aria-invalid={Boolean(errores.correo)}
          />
          {errores.correo && <p role="alert">{errores.correo}</p>}

          <label htmlFor="contrasena">Contraseña *</label>
          <input
            id="contrasena"
            type="password"
            value={contrasena}
            autoComplete="new-password"
            onChange={(e) => setContrasena(e.target.value)}
            aria-invalid={Boolean(errores.contrasena)}
          />
          {errores.contrasena && <p role="alert">{errores.contrasena}</p>}

          {errorGeneral && <p role="alert">{errorGeneral}</p>}

          <button type="submit" disabled={cargando}>
            {cargando ? 'Registrando...' : 'Crear cuenta'}
          </button>
        </form>
      </section>
    </main>
  )
}

export default RegistroPage
