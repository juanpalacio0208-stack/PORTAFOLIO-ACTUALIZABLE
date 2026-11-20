import { useState, type FormEvent } from 'react'
import { actualizarPerfil, type UsuarioAutenticado } from '../services/loginApi'

interface Props {
  usuario: UsuarioAutenticado
  onUsuarioActualizado: (usuario: UsuarioAutenticado) => void
}

export default function PerfilEditor({ usuario, onUsuarioActualizado }: Props) {
  const [editando, setEditando] = useState(false)
  const [procesando, setProcesando] = useState(false)
  const [nombre, setNombre] = useState(usuario.nombre_completo)
  const [correo, setCorreo] = useState(usuario.correo)
  const [contrasena, setContrasena] = useState('')
  const [confirmacion, setConfirmacion] = useState('')
  const [error, setError] = useState('')
  const [exito, setExito] = useState('')

  function cancelar() {
    setNombre(usuario.nombre_completo)
    setCorreo(usuario.correo)
    setContrasena('')
    setConfirmacion('')
    setError('')
    setEditando(false)
  }

  async function guardar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setError('')
    setExito('')

    if (contrasena && contrasena !== confirmacion) {
      setError('Las contrase?as no coinciden.')
      return
    }

    setProcesando(true)
    try {
      const actualizado = await actualizarPerfil({
        nombre_completo: nombre,
        correo,
        ...(contrasena ? { contrasena } : {}),
      })
      onUsuarioActualizado(actualizado)
      setNombre(actualizado.nombre_completo)
      setCorreo(actualizado.correo)
      setContrasena('')
      setConfirmacion('')
      setEditando(false)
      setExito('Perfil actualizado correctamente.')
    } catch (causa) {
      setError(
        causa instanceof Error
          ? causa.message
          : 'No fue posible actualizar el perfil.'
      )
    } finally {
      setProcesando(false)
    }
  }

  return <div className="perfil-editor">
    {editando ? (
      <form onSubmit={(evento) => void guardar(evento)}>
        <h2>Actualizar perfil</h2>

        <label htmlFor="perfil-nombre">Nombre completo</label>
        <input
          id="perfil-nombre"
          required
          minLength={3}
          maxLength={100}
          value={nombre}
          onChange={(evento) => setNombre(evento.target.value)}
        />

        <label htmlFor="perfil-correo">Correo electr?nico</label>
        <input
          id="perfil-correo"
          type="email"
          required
          value={correo}
          onChange={(evento) => setCorreo(evento.target.value)}
        />

        <label htmlFor="perfil-contrasena">
          Nueva contrase?a (opcional)
        </label>
        <input
          id="perfil-contrasena"
          type="password"
          minLength={8}
          autoComplete="new-password"
          value={contrasena}
          onChange={(evento) => setContrasena(evento.target.value)}
        />

        {contrasena && <>
          <label htmlFor="perfil-confirmacion">
            Confirmar contrase?a
          </label>
          <input
            id="perfil-confirmacion"
            type="password"
            required
            autoComplete="new-password"
            value={confirmacion}
            onChange={(evento) => setConfirmacion(evento.target.value)}
          />
        </>}

        {error && <p role="alert">{error}</p>}

        <button type="submit" disabled={procesando}>
          {procesando ? 'Guardando...' : 'Guardar cambios'}
        </button>
        <button type="button" disabled={procesando} onClick={cancelar}>
          Cancelar
        </button>
      </form>
    ) : (
      <button
        type="button"
        className="hu14-abrir"
        onClick={() => { setExito(''); setEditando(true) }}
      >
        Actualizar perfil
      </button>
    )}
    {exito && <p role="status">{exito}</p>}
  </div>
}
