
import type { Producto } from '../types/Producto'

const API_URL = 'http://127.0.0.1:8000'

interface ProductoBackend {
  id: number
  nombre: string
  descripcion: string
  categoria: string
  precio: number
  disponible: boolean
}

export async function obtenerProductos(): Promise<Producto[]> {
  const respuesta = await fetch(`${API_URL}/api/productos`)

  if (!respuesta.ok) {
    throw new Error('No fue posible cargar los productos.')
  }

  const productos: ProductoBackend[] = await respuesta.json()

  return productos.map((producto) => ({
    id: producto.id,
    nombre: producto.nombre,
    descripcion: producto.descripcion,
    precio: producto.precio,
    disponible: producto.disponible,
    imagen: `https://placehold.co/600x400?text=${encodeURIComponent(producto.nombre)}`,
  }))
}
