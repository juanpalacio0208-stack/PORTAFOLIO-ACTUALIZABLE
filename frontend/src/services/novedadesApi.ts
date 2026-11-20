import { API_URL } from './apiConfig'
const API = `${API_URL}/api`

async function peticion<T>(ruta: string, options: RequestInit = {}): Promise<T> {
  const respuesta = await fetch(`${API}${ruta}`, {
    credentials: 'include',
    ...options,
    headers: { 'Content-Type': 'application/json', ...options.headers },
  })
  if (!respuesta.ok) {
    const datos = await respuesta.json().catch(() => ({}))
    throw new Error(datos.detail || `Error HTTP ${respuesta.status}`)
  }
  return respuesta.json() as Promise<T>
}

export interface Notificacion {
  id: number
  tipo: string
  titulo: string
  mensaje: string
  creada: string
  leida: number
}
export interface HistorialSolicitud {
  id: string
  producto_nombre: string
  producto_id: number
  estado: string
  fecha_creacion: string
  fecha_actualizacion?: string
}
export const consentimiento = () => peticion<{autorizado: boolean}>('/notificaciones/consentimiento')
export const cambiarConsentimiento = (autorizado: boolean) => peticion<{autorizado: boolean}>('/notificaciones/consentimiento', {method: 'PUT', body: JSON.stringify({autorizado})})
export const notificaciones = () => peticion<Notificacion[]>('/notificaciones/mias')
export const marcarLeida = (id: number) => peticion<{mensaje: string}>(`/notificaciones/${id}/leida`, {method: 'PATCH'})
export const historial = () => peticion<HistorialSolicitud[]>('/solicitudes/mias')
export const enviar = (tipo: string, titulo: string, mensaje: string) => peticion<{destinatarios: number}>('/admin/notificaciones', {method: 'POST', body: JSON.stringify({tipo, titulo, mensaje})})

export const soyAdministradora = () => peticion<{administradora: boolean}>('/admin/notificaciones/permiso')
