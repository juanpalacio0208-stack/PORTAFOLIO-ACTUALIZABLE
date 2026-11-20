
import { API_URL } from './apiConfig'

export interface UsuarioAutenticado {
  id: number
  nombre_completo: string
  correo: string
  activo: boolean
  rol: 'usuario' | 'administrador'
}


export async function iniciarSesion(
  correo: string,
  contrasena: string
): Promise<UsuarioAutenticado> {
  const respuesta = await fetch(`${API_URL}/api/auth/login`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ correo, contrasena }),
  })

  if (respuesta.status === 401) {
    throw new Error('Correo electrÃ³nico o contraseÃ±a incorrectos.')
  }

  if (!respuesta.ok) {
    throw new Error('No fue posible iniciar sesiÃ³n.')
  }

  const datos = await respuesta.json()
  return datos.usuario as UsuarioAutenticado
}

export async function consultarSesion(): Promise<UsuarioAutenticado | null> {
  const respuesta = await fetch(`${API_URL}/api/auth/me`, {
    credentials: 'include',
  })

  if (respuesta.status === 401) return null

  if (!respuesta.ok) {
    throw new Error('No fue posible consultar la sesiÃ³n.')
  }

  return (await respuesta.json()) as UsuarioAutenticado
}

export async function cerrarSesion(): Promise<void> {
  const respuesta = await fetch(`${API_URL}/api/auth/logout`, {
    method: 'POST',
    credentials: 'include',
  })

  if (!respuesta.ok) {
    throw new Error('No fue posible cerrar sesiÃ³n.')
  }
}
