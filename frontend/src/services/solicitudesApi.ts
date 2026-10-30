
const API_URL = 'http://127.0.0.1:8000'

export interface SolicitudProducto {
  id: string
  producto_id: number
  producto_nombre: string
  estado: string
  fecha_creacion: string
}

export async function crearSolicitud(
  productoId: number
): Promise<SolicitudProducto> {
  const respuesta = await fetch(`${API_URL}/api/solicitudes`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      producto_id: productoId,
    }),
  })

  if (!respuesta.ok) {
    let mensaje = 'No fue posible crear la solicitud.'

    if (respuesta.status === 404) {
      mensaje = 'El producto seleccionado ya no existe.'
    } else if (respuesta.status === 409) {
      mensaje = 'El producto ya no está disponible.'
    }

    throw new Error(mensaje)
  }

  return (await respuesta.json()) as SolicitudProducto
}
