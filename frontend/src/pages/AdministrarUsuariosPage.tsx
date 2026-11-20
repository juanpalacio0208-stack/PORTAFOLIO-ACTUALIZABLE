import { useEffect, useState } from 'react'
import { actualizarUsuarioAdmin, consultarUsuarios } from '../services/usuariosAdminApi'
import type { UsuarioAutenticado } from '../services/loginApi'
import '../login.css'

function AdministrarUsuariosPage({ volver }: { volver: () => void }) {
  const [usuarios, setUsuarios] = useState<UsuarioAutenticado[]>([])
  const [error, setError] = useState('')
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    consultarUsuarios().then(setUsuarios)
      .catch((causa: unknown) => setError(causa instanceof Error ? causa.message : 'Error al cargar usuarios.'))
      .finally(() => setCargando(false))
  }, [])

  async function cambiar(id: number, cambios: { activo?: boolean; rol?: 'usuario' | 'administrador' }) {
    setError('')
    try {
      const actualizado = await actualizarUsuarioAdmin(id, cambios)
      setUsuarios((lista) => lista.map((usuario) => usuario.id === id ? actualizado : usuario))
    } catch (causa) {
      setError(causa instanceof Error ? causa.message : 'No fue posible actualizar el usuario.')
    }
  }

  return <main className="login-contenedor hu13-contenedor"><section className="login-tarjeta hu13-tarjeta">
    <button type="button" className="login-volver" onClick={volver}>← Volver a mi cuenta</button>
    <h1>Administrar usuarios</h1>
    <p>Gestiona el rol y el acceso de las cuentas registradas.</p>
    {error && <p role="alert">{error}</p>}
    {cargando ? <p role="status">Cargando usuarios…</p> : <div className="hu13-tabla-wrap"><table className="hu13-tabla">
      <thead><tr><th>Nombre</th><th>Correo</th><th>Rol</th><th>Estado</th><th>Acciones</th></tr></thead>
      <tbody>{usuarios.map((usuario) => <tr key={usuario.id}>
        <td>{usuario.nombre_completo}</td><td>{usuario.correo}</td>
        <td><select aria-label={`Rol de ${usuario.nombre_completo}`} value={usuario.rol} onChange={(evento) => void cambiar(usuario.id, { rol: evento.target.value as 'usuario' | 'administrador' })}><option value="usuario">Usuario</option><option value="administrador">Administrador</option></select></td>
        <td>{usuario.activo ? 'Activo' : 'Inactivo'}</td>
        <td><button type="button" onClick={() => void cambiar(usuario.id, { activo: !usuario.activo })}>{usuario.activo ? 'Desactivar' : 'Activar'}</button></td>
      </tr>)}</tbody>
    </table></div>}
  </section></main>
}

export default AdministrarUsuariosPage
