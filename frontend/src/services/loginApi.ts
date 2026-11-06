
const API_URL = 'http://127.0.0.1:8000'

export interface UsuarioAutenticado {
  id: number
  nombre_completo: string
  correo: string
  activo: boolean
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
    throw new Error('Correo electrónico o contraseña incorrectos.')
  }

  if (!respuesta.ok) {
    throw new Error('No fue posible iniciar sesión.')
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
    throw new Error('No fue posible consultar la sesión.')
  }

  return (await respuesta.json()) as UsuarioAutenticado
}

export async function cerrarSesion(): Promise<void> {
  const respuesta = await fetch(`${API_URL}/api/auth/logout`, {
    method: 'POST',
    credentials: 'include',
  })

  if (!respuesta.ok) {
    throw new Error('No fue posible cerrar sesión.')
  }
}
