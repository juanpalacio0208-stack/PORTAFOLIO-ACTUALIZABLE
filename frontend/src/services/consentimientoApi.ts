import { API_URL } from './apiConfig'

export interface ConsentimientoNotificaciones {
  autorizado: boolean
  actualizado_en: string | null
}

async function leerRespuesta(respuesta: Response): Promise<ConsentimientoNotificaciones> {
  if (respuesta.status === 401 || respuesta.status === 403) {
    throw new Error('Tu sesión ha vencido. Inicia sesión nuevamente.')
  }
  if (!respuesta.ok) {
    throw new Error('No fue posible consultar o guardar tus preferencias.')
  }
  return (await respuesta.json()) as ConsentimientoNotificaciones
}

export async function consultarConsentimiento(): Promise<ConsentimientoNotificaciones> {
  const respuesta = await fetch(`${API_URL}/api/notificaciones/consentimiento`, {
    credentials: 'include',
  })
  return leerRespuesta(respuesta)
}

export async function guardarConsentimiento(autorizado: boolean): Promise<ConsentimientoNotificaciones> {
  const respuesta = await fetch(`${API_URL}/api/notificaciones/consentimiento`, {
    method: 'PATCH',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ autorizado }),
  })
  return leerRespuesta(respuesta)
}
