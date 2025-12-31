import { Radar, TrendingUp, Lock, MessageCircle, Search, Zap, Target, Eye } from 'lucide-react'

// Datos de demo (después vendrán de la API)
const demoProducts = [
  {
    id: 1,
    name: "Serum Vitamina C Premium",
    image: "https://via.placeholder.com/300x300/111827/00ff88?text=Serum",
    sales7d: 847,
    sales30d: 2340,
    stock: 1250,
    price: 45000,
    margin: 62,
    score: 8.5,
    country: "CO",
    trend: "up",
  },
  {
    id: 2,
    name: "Faja Colombiana Reductora",
    image: "https://via.placeholder.com/300x300/111827/00ff88?text=Faja",
    sales7d: 623,
    sales30d: 1890,
    stock: 890,
    price: 89000,
    margin: 55,
    score: 7.8,
    country: "CO",
    trend: "up",
  },
  {
    id: 3,
    name: "Auriculares Bluetooth Pro",
    image: "https://via.placeholder.com/300x300/111827/00ff88?text=Auriculares",
    sales7d: 412,
    sales30d: 1456,
    stock: 2100,
    price: 65000,
    margin: 48,
    score: 6.9,
    country: "CO",
    trend: "stable",
  },
  {
    id: 4,
    name: "Plancha Alisadora Profesional",
    image: "https://via.placeholder.com/300x300/111827/00ff88?text=Plancha",
    sales7d: 389,
    sales30d: 1234,
    stock: 567,
    price: 125000,
    margin: 58,
    score: 7.2,
    country: "CO",
    trend: "up",
  },
]

function ScoreBadge({ score }: { score: number }) {
  const getScoreColor = (s: number) => {
    if (s >= 8) return 'text-radar-accent bg-radar-accent/10 border-radar-accent/30'
    if (s >= 6) return 'text-radar-warning bg-radar-warning/10 border-radar-warning/30'
    return 'text-radar-danger bg-radar-danger/10 border-radar-danger/30'
  }

  const getScoreEmoji = (s: number) => {
    if (s >= 8) return '🟢'
    if (s >= 6) return '🟡'
    return '🔴'
  }

  return (
    <div className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border font-mono text-sm font-bold ${getScoreColor(score)}`}>
      <span>{getScoreEmoji(score)}</span>
      <span className="score-glow">{score.toFixed(1)}</span>
    </div>
  )
}

function ProductCard({ product, index }: { product: typeof demoProducts[0], index: number }) {
  return (
    <div 
      className="card-glow bg-radar-card border border-radar-border rounded-xl overflow-hidden transition-all duration-300 hover:border-radar-accent/50 hover:shadow-lg hover:shadow-radar-accent/10"
      style={{ animationDelay: `${index * 100}ms` }}
    >
      {/* Image */}
      <div className="relative aspect-square bg-radar-dark">
        <img 
          src={product.image} 
          alt={product.name}
          className="w-full h-full object-cover"
        />
        <div className="absolute top-3 right-3">
          <ScoreBadge score={product.score} />
        </div>
        <div className="absolute top-3 left-3 bg-radar-dark/80 backdrop-blur-sm px-2 py-1 rounded text-xs font-mono">
          🇨🇴 {product.country}
        </div>
      </div>

      {/* Content */}
      <div className="p-4 space-y-4">
        <h3 className="font-semibold text-lg line-clamp-2 leading-tight">
          {product.name}
        </h3>

        {/* Stats Grid - GRATIS */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-radar-dark/50 rounded-lg p-3">
            <div className="text-xs text-gray-400 mb-1">Ventas 7d</div>
            <div className="font-mono font-bold text-radar-accent flex items-center gap-1">
              {product.sales7d.toLocaleString()}
              {product.trend === 'up' && <TrendingUp className="w-3 h-3" />}
            </div>
          </div>
          <div className="bg-radar-dark/50 rounded-lg p-3">
            <div className="text-xs text-gray-400 mb-1">Ventas 30d</div>
            <div className="font-mono font-bold">{product.sales30d.toLocaleString()}</div>
          </div>
          <div className="bg-radar-dark/50 rounded-lg p-3">
            <div className="text-xs text-gray-400 mb-1">Stock</div>
            <div className="font-mono font-bold">{product.stock.toLocaleString()}</div>
          </div>
          <div className="bg-radar-dark/50 rounded-lg p-3">
            <div className="text-xs text-gray-400 mb-1">Precio</div>
            <div className="font-mono font-bold">${(product.price / 1000).toFixed(0)}k</div>
          </div>
        </div>

        {/* Locked Content */}
        <div className="relative">
          <div className="blur-locked space-y-3 select-none">
            <div className="bg-radar-dark/50 rounded-lg p-3">
              <div className="text-xs text-gray-400 mb-1">Margen Estimado</div>
              <div className="font-mono font-bold text-radar-accent">{product.margin}%</div>
            </div>
            <div className="bg-radar-dark/50 rounded-lg p-3">
              <div className="text-xs text-gray-400 mb-1">Por qué este score</div>
              <div className="text-sm">Alta demanda, bajo inventario competencia...</div>
            </div>
            <div className="bg-radar-dark/50 rounded-lg p-3">
              <div className="text-xs text-gray-400 mb-1">Ángulos de Venta</div>
              <div className="text-sm">• Resultados en 7 días • Envío gratis...</div>
            </div>
          </div>

          {/* Lock Overlay */}
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-radar-card/80 backdrop-blur-sm rounded-lg">
            <Lock className="w-8 h-8 text-radar-accent mb-3" />
            <p className="text-sm text-gray-400 mb-4 text-center px-4">
              Desbloquea el análisis completo
            </p>
            <a
              href="https://wa.me/34614696857?text=Hola%20Andrés%2C%20vi%20Estrategas%20IA%20Tools%20y%20quiero%20ser%20parte%20de%20la%20comunidad"
              target="_blank"
              rel="noopener noreferrer"
              className="whatsapp-pulse inline-flex items-center gap-2 bg-[#25D366] hover:bg-[#20bd5a] text-white font-semibold px-4 py-2.5 rounded-lg transition-colors"
            >
              <MessageCircle className="w-5 h-5" />
              Habla con Andrés
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}

function Header() {
  return (
    <header className="border-b border-radar-border bg-radar-dark/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative">
              <Radar className="w-10 h-10 text-radar-accent" />
              <div className="absolute inset-0 animate-ping">
                <Radar className="w-10 h-10 text-radar-accent opacity-20" />
              </div>
            </div>
            <div>
              <h1 className="text-xl font-bold gradient-text">Estrategas IA</h1>
              <p className="text-xs text-gray-500">by Trucos Ecomm & Drop</p>
            </div>
          </div>

          <nav className="hidden md:flex items-center gap-6">
            <a href="#productos" className="text-gray-400 hover:text-radar-accent transition-colors flex items-center gap-2">
              <Search className="w-4 h-4" />
              Productos
            </a>
            <a href="#creativos" className="text-gray-400 hover:text-radar-accent transition-colors flex items-center gap-2">
              <Eye className="w-4 h-4" />
              Creativos
            </a>
            <a
              href="https://wa.me/34614696857?text=Hola%20Andrés%2C%20quiero%20info%20sobre%20la%20comunidad"
              target="_blank"
              rel="noopener noreferrer"
              className="bg-radar-accent/10 border border-radar-accent/30 text-radar-accent px-4 py-2 rounded-lg hover:bg-radar-accent/20 transition-colors flex items-center gap-2"
            >
              <Zap className="w-4 h-4" />
              Únete
            </a>
          </nav>
        </div>
      </div>
    </header>
  )
}

function Hero() {
  return (
    <section className="py-16 md:py-24 px-4">
      <div className="max-w-4xl mx-auto text-center">
        <div className="inline-flex items-center gap-2 bg-radar-accent/10 border border-radar-accent/30 text-radar-accent px-4 py-2 rounded-full text-sm font-medium mb-6">
          <Target className="w-4 h-4" />
          Product Research con IA
        </div>

        <h1 className="text-4xl md:text-6xl font-bold mb-6 leading-tight">
          Encuentra productos
          <span className="gradient-text block">ganadores en minutos</span>
        </h1>

        <p className="text-xl text-gray-400 mb-8 max-w-2xl mx-auto">
          Analiza ventas reales, descubre creativos que funcionan y obtén ángulos de venta probados. 
          Todo en una sola herramienta.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <a href="#productos" className="btn-primary inline-flex items-center justify-center gap-2">
            <Search className="w-5 h-5" />
            Ver Productos
          </a>
          <a
            href="https://wa.me/34614696857?text=Hola%20Andrés%2C%20vi%20Estrategas%20IA%20Tools%20y%20quiero%20ser%20parte%20de%20la%20comunidad"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center gap-2 bg-radar-card border border-radar-border text-white px-6 py-3 rounded-lg hover:border-radar-accent/50 transition-colors"
          >
            <MessageCircle className="w-5 h-5" />
            Acceso Completo
          </a>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-8 mt-16 max-w-2xl mx-auto">
          <div>
            <div className="text-3xl md:text-4xl font-bold gradient-text">500K+</div>
            <div className="text-sm text-gray-500">Productos analizados</div>
          </div>
          <div>
            <div className="text-3xl md:text-4xl font-bold gradient-text">11K+</div>
            <div className="text-sm text-gray-500">Creativos indexados</div>
          </div>
          <div>
            <div className="text-3xl md:text-4xl font-bold gradient-text">12</div>
            <div className="text-sm text-gray-500">Países LATAM</div>
          </div>
        </div>
      </div>
    </section>
  )
}

function FeaturesSection() {
  const features = [
    {
      icon: TrendingUp,
      title: "Ventas Reales",
      description: "Datos de ventas verificados de Dropi, no estimaciones.",
      free: true,
    },
    {
      icon: Eye,
      title: "Creativos Competencia",
      description: "Videos y ángulos que ya están funcionando en Meta y TikTok.",
      free: false,
    },
    {
      icon: Target,
      title: "Análisis IA",
      description: "Score de viabilidad, saturación y precio recomendado.",
      free: false,
    },
    {
      icon: Zap,
      title: "Ángulos de Venta",
      description: "Hooks y triggers emocionales probados para tu copy.",
      free: false,
    },
  ]

  return (
    <section className="py-16 px-4 border-t border-radar-border">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-2xl md:text-3xl font-bold text-center mb-12">
          Todo lo que necesitas para <span className="gradient-text">vender más</span>
        </h2>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, i) => (
            <div 
              key={i}
              className="bg-radar-card border border-radar-border rounded-xl p-6 hover:border-radar-accent/30 transition-colors relative overflow-hidden"
            >
              {!feature.free && (
                <div className="absolute top-3 right-3">
                  <Lock className="w-4 h-4 text-radar-accent" />
                </div>
              )}
              <feature.icon className="w-10 h-10 text-radar-accent mb-4" />
              <h3 className="font-semibold text-lg mb-2">{feature.title}</h3>
              <p className="text-gray-400 text-sm">{feature.description}</p>
              <div className="mt-4">
                <span className={`text-xs px-2 py-1 rounded-full ${feature.free ? 'bg-radar-accent/10 text-radar-accent' : 'bg-radar-border text-gray-400'}`}>
                  {feature.free ? '✓ Gratis' : '🔒 Comunidad'}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

function ProductsSection() {
  return (
    <section id="productos" className="py-16 px-4 border-t border-radar-border">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-2xl md:text-3xl font-bold mb-2">
              🔥 Productos <span className="gradient-text">Trending</span>
            </h2>
            <p className="text-gray-400">Top productos con más ventas esta semana</p>
          </div>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {demoProducts.map((product, index) => (
            <ProductCard key={product.id} product={product} index={index} />
          ))}
        </div>

        {/* CTA */}
        <div className="mt-12 text-center">
          <div className="bg-radar-card border border-radar-border rounded-xl p-8 max-w-2xl mx-auto">
            <Lock className="w-12 h-12 text-radar-accent mx-auto mb-4" />
            <h3 className="text-xl font-bold mb-2">¿Quieres ver más productos?</h3>
            <p className="text-gray-400 mb-6">
              Accede a +500,000 productos con filtros avanzados, análisis completo y creativos descargables.
            </p>
            <a
              href="https://wa.me/34614696857?text=Hola%20Andrés%2C%20vi%20Estrategas%20IA%20Tools%20y%20quiero%20acceso%20completo%20a%20los%20productos"
              target="_blank"
              rel="noopener noreferrer"
              className="whatsapp-pulse inline-flex items-center gap-2 bg-[#25D366] hover:bg-[#20bd5a] text-white font-semibold px-6 py-3 rounded-lg transition-colors"
            >
              <MessageCircle className="w-5 h-5" />
              Habla con Andrés por WhatsApp
            </a>
          </div>
        </div>
      </div>
    </section>
  )
}

function Footer() {
  return (
    <footer className="border-t border-radar-border py-8 px-4">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <Radar className="w-6 h-6 text-radar-accent" />
          <span className="font-semibold">Estrategas IA Tools</span>
        </div>
        <p className="text-gray-500 text-sm">
          © 2024 Trucos Ecomm & Drop. Todos los derechos reservados.
        </p>
        <a
          href="https://wa.me/34614696857"
          target="_blank"
          rel="noopener noreferrer"
          className="text-radar-accent hover:underline text-sm"
        >
          Contacto
        </a>
      </div>
    </footer>
  )
}

export default function HomePage() {
  return (
    <main>
      <Header />
      <Hero />
      <FeaturesSection />
      <ProductsSection />
      <Footer />
    </main>
  )
}
