import type { UsuarioAutenticado } from './loginApi'

import { API_URL } from './apiConfig'

export async function consultarUsuarios(): Promise<UsuarioAutenticado[]> {
  const respuesta = await fetch(`${API_URL}/api/admin/usuarios`, { credentials: 'include' })
  if (!respuesta.ok) throw new Error('No fue posible cargar los usuarios.')
  return (await respuesta.json()) as UsuarioAutenticado[]
}

export async function actualizarUsuarioAdmin(id: number, cambios: { activo?: boolean; rol?: 'usuario' | 'administrador' }): Promise<UsuarioAutenticado> {
  const respuesta = await fetch(`${API_URL}/api/admin/usuarios/${id}`, {
    method: 'PATCH', credentials: 'include',
    headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(cambios),
  })
  if (!respuesta.ok) {
    const datos = await respuesta.json().catch(() => null)
    throw new Error(datos?.detail ?? 'No fue posible actualizar el usuario.')
  }
  return (await respuesta.json()) as UsuarioAutenticado
}
