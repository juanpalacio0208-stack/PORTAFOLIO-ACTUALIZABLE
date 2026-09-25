import ProductoCard from '../components/ProductoCard'
import { productos } from '../data/Productos'

function PortafolioPage() {
  const productosDisponibles = productos.filter(
    (producto) => producto.disponible,
  )

  return (
    <>
      <header className="header">
        <div className="contenedor navegacion">
          <a href="#inicio" className="logo">
            Portafolio
          </a>

          <nav>
            <a href="#inicio">Inicio</a>
            <a href="#productos">Productos</a>

            <button type="button" className="boton-ingresar">
              Ingresar
            </button>
          </nav>
        </div>
      </header>

      <main>
        <section className="hero" id="inicio">
          <div className="contenedor">
            <span className="hero-etiqueta">
              Productos importados
            </span>

            <h1>
              Encuentra productos seleccionados para ti
            </h1>

            <p>
              Explora nuestro portafolio y conoce los productos
              disponibles actualmente.
            </p>

            <a href="#productos" className="boton-principal">
              Ver productos
            </a>
          </div>
        </section>

        <section className="productos-seccion" id="productos">
          <div className="contenedor">
            <div className="titulo-seccion">
              <span>Nuestro catálogo</span>

              <h2>Productos disponibles</h2>

              <p>
                Conoce los productos disponibles para la venta.
              </p>
            </div>

            {productosDisponibles.length > 0 ? (
              <div className="productos-grid">
                {productosDisponibles.map((producto) => (
                  <ProductoCard
                    key={producto.id}
                    producto={producto}
                  />
                ))}
              </div>
            ) : (
              <div className="sin-productos">
                <h3>No hay productos disponibles</h3>

                <p>
                  Pronto tendremos nuevos productos para ti.
                </p>
              </div>
            )}
          </div>
        </section>
      </main>

      <footer>
        <div className="contenedor">
          <strong>Portafolio Actualizable</strong>

          <p>
            Productos importados seleccionados para ti.
          </p>
        </div>
      </footer>
    </>
  )
}

export default PortafolioPage