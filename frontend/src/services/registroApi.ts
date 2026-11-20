
export interface DatosRegistro {
  nombre_completo: string
  correo: string
  contrasena: string
}

export interface UsuarioRegistrado {
  id: number
  nombre_completo: string
  correo: string
  activo: boolean
}

export async function registrarUsuario(
  datos: DatosRegistro
): Promise<UsuarioRegistrado> {
  let respuesta: Response

  try {
    respuesta = await fetch('http://localhost:8000/api/auth/registro', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(datos),
    })
  } catch {
    throw new Error('No se pudo conectar con el servidor.')
  }

  if (respuesta.status === 409) {
    throw new Error('Este correo electrónico ya está registrado.')
  }

  if (respuesta.status === 422) {
    throw new Error('Revisa los campos del formulario.')
  }

  if (!respuesta.ok) {
    throw new Error('No fue posible completar el registro.')
  }

  return (await respuesta.json()) as UsuarioRegistrado
}
