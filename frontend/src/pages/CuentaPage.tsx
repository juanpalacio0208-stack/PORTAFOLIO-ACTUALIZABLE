import { useEffect, useState } from 'react'
import { cerrarSesion, type UsuarioAutenticado } from '../services/loginApi'
import { consentimiento, cambiarConsentimiento, notificaciones, marcarLeida, historial, enviar, soyAdministradora, type Notificacion, type HistorialSolicitud } from '../services/novedadesApi'
import PerfilEditor from './PerfilEditor'
import '../login.css'
import '../novedades.css'
import '../consentimiento.css'

interface Props { usuario: UsuarioAutenticado; onLogout: () => void; volverCatalogo?: () => void; onPreferencias: () => void; onAdministrarUsuarios: () => void; onUsuarioActualizado: (usuario: UsuarioAutenticado) => void }

export default function CuentaPage({ usuario, onLogout, volverCatalogo, onPreferencias, onAdministrarUsuarios, onUsuarioActualizado }: Props) {
  const [error, setError] = useState('')
  const [aviso, setAviso] = useState('')
  const [permiso, setPermiso] = useState(false)
  const [mensajes, setMensajes] = useState<Notificacion[]>([])
  const [pedidos, setPedidos] = useState<HistorialSolicitud[]>([])
  const [cargando, setCargando] = useState(true)
  const [tipo, setTipo] = useState('nuevo_producto')
  const [titulo, setTitulo] = useState('')
  const [mensaje, setMensaje] = useState('')
  const [administradora, setAdministradora] = useState(false)
  const [puedeEnviar, setPuedeEnviar] = useState(true)

  async function actualizar() {
    const [c, n, h] = await Promise.all([consentimiento(), notificaciones(), historial()])
    setPermiso(c.autorizado); setMensajes(n); setPedidos(h)
  }
  useEffect(() => {
    let activo = true
    soyAdministradora().then(() => { if (activo) setAdministradora(true) }).catch(() => {})
    Promise.all([consentimiento(), notificaciones(), historial()]).then(([c,n,h]) => {
      if (!activo) return
      setPermiso(c.autorizado); setMensajes(n); setPedidos(h)
    }).catch(e => { if (activo) setError(e instanceof Error ? e.message : 'No se pudo cargar la cuenta') })
      .finally(() => { if (activo) setCargando(false) })
    return () => { activo = false }
  }, [])
  async function ejecutar(tarea: () => Promise<unknown>, exito: string) {
    setError(''); setAviso('')
    try { await tarea(); await actualizar(); setAviso(exito) }
    catch(e) { setError(e instanceof Error ? e.message : 'Ocurrió un error') }
  }
  return <main className="login-contenedor"><div className="cuenta-contenido">
    <section className="login-tarjeta">
      <h1>Mi cuenta</h1><p>Bienvenido, <strong>{usuario.nombre_completo}</strong>.</p><p>{usuario.correo}</p>
      {usuario.rol === 'administrador' && (
        <button type="button" className="hu14-abrir" onClick={onAdministrarUsuarios}>
          Administrar usuarios
        </button>
      )}
      <PerfilEditor
        usuario={usuario}
        onUsuarioActualizado={onUsuarioActualizado}
      />
      <button type="button" className="hu14-abrir" onClick={onPreferencias}>Preferencias de notificaciones</button>
      {volverCatalogo && <button type="button" onClick={volverCatalogo}>Volver al catálogo</button>}
      <button type="button" onClick={() => void ejecutar(async () => { await cerrarSesion(); onLogout() }, 'Sesión cerrada')}>Cerrar sesión</button>
      {error && <p role="alert">{error}</p>}{aviso && <p role="status">{aviso}</p>}
    </section>
    <section className="login-tarjeta">
      <h2>Mis notificaciones</h2>
      <label className="permiso"><input type="checkbox" checked={permiso} onChange={e => void ejecutar(async () => { await cambiarConsentimiento(e.target.checked) }, 'Preferencia guardada')} /> Autorizo recibir novedades y promociones</label>
      <p>Los mensajes llegan a esta bandeja dentro de la aplicación, no a tu correo.</p>
      <button type="button" onClick={() => void ejecutar(actualizar, 'Bandeja actualizada')}>Actualizar bandeja</button>
      {cargando ? <p>Cargando...</p> : mensajes.length === 0 ? <p>No hay notificaciones.</p> : <ul className="novedades-lista">{mensajes.map(n => <li key={n.id}><strong>{n.titulo}</strong> <small>{n.creada}</small><p>{n.mensaje}</p>{!n.leida && <button type="button" onClick={() => void ejecutar(() => marcarLeida(n.id), 'Notificación leída')}>Marcar leída</button>}</li>)}</ul>}
    </section>
    <section className="login-tarjeta"><h2>Mis solicitudes</h2>
      <p>Solo se muestran solicitudes realizadas mientras tenías tu sesión iniciada.</p>
      {pedidos.length === 0 ? <p>Aún no tienes solicitudes asociadas a tu cuenta.</p> : <ul className="novedades-lista">{pedidos.map(p => <li key={p.id}><strong>{p.producto_nombre}</strong><p>Estado: {p.estado}</p><small>Solicitud: {p.id} · {p.fecha_creacion}</small></li>)}</ul>}
    </section>
    {administradora && <section className="login-tarjeta"><h2>Enviar promociones</h2>
      <p>Exclusivo para administradora autorizada. Los demás usuarios recibirán un error 403.</p>
      {puedeEnviar && <form onSubmit={e => {e.preventDefault(); void ejecutar(async () => {const r = await enviar(tipo,titulo,mensaje); setTitulo(''); setMensaje(''); void r }, 'Envío procesado')}}>
        <label>Tipo<select value={tipo} onChange={e => setTipo(e.target.value)}><option value="nuevo_producto">Nuevo producto</option><option value="descuento">Descuento</option><option value="promocion">Promoción</option></select></label>
        <label>Título<input value={titulo} required minLength={3} maxLength={120} onChange={e => setTitulo(e.target.value)}/></label>
        <label>Mensaje<textarea value={mensaje} required minLength={3} maxLength={1000} onChange={e => setMensaje(e.target.value)}/></label>
        <button type="submit">Enviar a usuarios autorizados</button>
        <button type="button" onClick={() => setPuedeEnviar(false)}>Ocultar formulario</button>
      </form>}{!puedeEnviar && <button type="button" onClick={() => setPuedeEnviar(true)}>Mostrar formulario</button>}
    </section>}
  </div></main>
}
