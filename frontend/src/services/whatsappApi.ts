import type { DatosContacto } from './contactoApi'

export interface DatosSolicitudWhatsApp {
  solicitudId: string
  productoNombre: string
  contacto: DatosContacto
}

export function construirMensajeWhatsApp({
  solicitudId,
  productoNombre,
  contacto,
}: DatosSolicitudWhatsApp): string {
  const lineas = [
    'Hola, Laura. Quiero solicitar el siguiente producto:',
    `Producto: ${productoNombre}`,
    `Número de solicitud: ${solicitudId}`,
    `Nombre: ${contacto.nombre_completo}`,
    `Teléfono / WhatsApp: ${contacto.telefono}`,
  ]

  if (contacto.correo?.trim()) {
    lineas.push(`Correo: ${contacto.correo.trim()}`)
  }

  lineas.push('Quedo pendiente de tu respuesta. ¡Muchas gracias!')
  return lineas.join('\n')
}

/**
 * El teléfono de destino se configura en frontend/.env.local.
 * Debe incluir indicativo de país, sin '+' ni espacios. Ej.: 57 + teléfono colombiano.
 * Retorna null si aún no se configuró un número válido.
 */
export function generarEnlaceWhatsApp(datos: DatosSolicitudWhatsApp): string | null {
  const numero = String(import.meta.env.VITE_WHATSAPP_LAURA ?? '').replace(/\D/g, '')
  if (!/^[1-9]\d{7,14}$/.test(numero)) return null

  const texto = encodeURIComponent(construirMensajeWhatsApp(datos))
  return `https://wa.me/${numero}?text=${texto}`
}
