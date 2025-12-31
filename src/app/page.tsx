import { Radar, TrendingUp, Lock, MessageCircle, Search, Zap, Target, Eye, Unlock, Play, Download, Users, DollarSign, BarChart3, Sparkles } from 'lucide-react'

// Datos de demo con imágenes reales
const demoProducts = [
  {
    id: 1,
    name: "Serum Vitamina C Premium",
    image: "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=400&h=400&fit=crop",
    sales7d: 847,
    sales30d: 2340,
    stock: 1250,
    price: 45000,
    margin: 62,
    score: 8.5,
    country: "CO",
    trend: "up",
    category: "Skincare",
  },
  {
    id: 2,
    name: "Faja Colombiana Reductora",
    image: "https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=400&h=400&fit=crop",
    sales7d: 623,
    sales30d: 1890,
    stock: 890,
    price: 89000,
    margin: 55,
    score: 7.8,
    country: "CO",
    trend: "up",
    category: "Moda",
  },
  {
    id: 3,
    name: "Auriculares Bluetooth Pro",
    image: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop",
    sales7d: 412,
    sales30d: 1456,
    stock: 2100,
    price: 65000,
    margin: 48,
    score: 6.9,
    country: "CO",
    trend: "stable",
    category: "Tech",
  },
  {
    id: 4,
    name: "Plancha Alisadora Profesional",
    image: "https://images.unsplash.com/photo-1522338242042-2d1c9cd60fc7?w=400&h=400&fit=crop",
    sales7d: 389,
    sales30d: 1234,
    stock: 567,
    price: 125000,
    margin: 58,
    score: 7.2,
    country: "CO",
    trend: "up",
    category: "Belleza",
  },
]

// Producto ejemplo premium (desbloqueado)
const premiumProductExample = {
  id: 99,
  name: "Corrector de Postura Premium",
  image: "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=400&fit=crop",
  sales7d: 1247,
  sales30d: 4890,
  stock: 3200,
  price: 55000,
  margin: 67,
  score: 9.2,
  country: "CO",
  trend: "up",
  category: "Salud",
  // Datos premium
  scoreReason: "Alta demanda creciente (+45% vs semana pasada), margen excelente (67%), baja competencia en Meta (solo 12 anunciantes activos), proveedor verificado con 98% de entregas exitosas.",
  salesAngles: [
    { angle: "Dolor de espalda", effectiveness: 92 },
    { angle: "Home office", effectiveness: 87 },
    { angle: "Resultados en 7 días", effectiveness: 78 },
  ],
  emotionalTriggers: ["Alivio del dolor", "Confianza", "Bienestar"],
  targetAudience: {
    age: "25-45",
    gender: "Unisex",
    interests: ["Fitness", "Trabajo remoto", "Salud"],
  },
  competitors: 12,
  avgPrice: 65000,
  recommendedPrice: 59900,
}

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
      <div className="relative aspect-square bg-radar-dark overflow-hidden">
        <img 
          src={product.image} 
          alt={product.name}
          className="w-full h-full object-cover transition-transform duration-300 hover:scale-105"
        />
        <div className="absolute top-3 right-3">
          <ScoreBadge score={product.score} />
        </div>
        <div className="absolute top-3 left-3 bg-radar-dark/80 backdrop-blur-sm px-2 py-1 rounded text-xs font-mono">
          🇨🇴 {product.country}
        </div>
        <div className="absolute bottom-3 left-3 bg-radar-accent/90 text-radar-dark px-2 py-1 rounded text-xs font-semibold">
          {product.category}
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

// Componente de producto PREMIUM (desbloqueado)
function PremiumProductCard() {
  const product = premiumProductExample
  
  return (
    <div className="bg-gradient-to-br from-radar-card to-radar-dark border-2 border-radar-accent/50 rounded-2xl overflow-hidden shadow-lg shadow-radar-accent/20">
      <div className="grid lg:grid-cols-2 gap-0">
        {/* Left - Image & Basic Info */}
        <div className="p-6 space-y-6">
          <div className="relative aspect-square rounded-xl overflow-hidden">
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
            <div className="absolute bottom-3 left-3 bg-radar-accent/90 text-radar-dark px-2 py-1 rounded text-xs font-semibold">
              {product.category}
            </div>
            {/* Unlocked Badge */}
            <div className="absolute bottom-3 right-3 bg-radar-accent text-radar-dark px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1">
              <Unlock className="w-3 h-3" />
              PREMIUM
            </div>
          </div>

          <div>
            <h3 className="font-bold text-2xl mb-4">{product.name}</h3>
            
            {/* Stats Grid */}
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-radar-dark/50 rounded-lg p-3">
                <div className="text-xs text-gray-400 mb-1">Ventas 7d</div>
                <div className="font-mono font-bold text-radar-accent flex items-center gap-1">
                  {product.sales7d.toLocaleString()}
                  <TrendingUp className="w-3 h-3" />
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
                <div className="text-xs text-gray-400 mb-1">Margen</div>
                <div className="font-mono font-bold text-radar-accent">{product.margin}%</div>
              </div>
            </div>
          </div>
        </div>

        {/* Right - Premium Analysis */}
        <div className="bg-radar-dark/30 p-6 space-y-5 border-l border-radar-border">
          <div className="flex items-center gap-2 text-radar-accent font-semibold">
            <Sparkles className="w-5 h-5" />
            Análisis IA Completo
          </div>

          {/* Score Reason */}
          <div className="bg-radar-card/50 rounded-lg p-4">
            <div className="text-xs text-radar-accent mb-2 font-semibold">¿Por qué {product.score}/10?</div>
            <p className="text-sm text-gray-300 leading-relaxed">{product.scoreReason}</p>
          </div>

          {/* Sales Angles */}
          <div className="bg-radar-card/50 rounded-lg p-4">
            <div className="text-xs text-radar-accent mb-3 font-semibold">🎯 Ángulos de Venta</div>
            <div className="space-y-2">
              {product.salesAngles.map((angle, i) => (
                <div key={i} className="flex items-center justify-between">
                  <span className="text-sm">{angle.angle}</span>
                  <div className="flex items-center gap-2">
                    <div className="w-20 h-2 bg-radar-border rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-radar-accent rounded-full"
                        style={{ width: `${angle.effectiveness}%` }}
                      />
                    </div>
                    <span className="text-xs font-mono text-radar-accent">{angle.effectiveness}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Emotional Triggers */}
          <div className="bg-radar-card/50 rounded-lg p-4">
            <div className="text-xs text-radar-accent mb-3 font-semibold">💡 Triggers Emocionales</div>
            <div className="flex flex-wrap gap-2">
              {product.emotionalTriggers.map((trigger, i) => (
                <span key={i} className="bg-radar-accent/10 text-radar-accent px-3 py-1 rounded-full text-xs">
                  {trigger}
                </span>
              ))}
            </div>
          </div>

          {/* Target & Pricing */}
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-radar-card/50 rounded-lg p-4">
              <div className="text-xs text-gray-400 mb-1 flex items-center gap-1">
                <Users className="w-3 h-3" /> Target
              </div>
              <div className="text-sm font-semibold">{product.targetAudience.age}</div>
              <div className="text-xs text-gray-400">{product.targetAudience.gender}</div>
            </div>
            <div className="bg-radar-card/50 rounded-lg p-4">
              <div className="text-xs text-gray-400 mb-1 flex items-center gap-1">
                <BarChart3 className="w-3 h-3" /> Competidores
              </div>
              <div className="text-sm font-semibold">{product.competitors} activos</div>
              <div className="text-xs text-gray-400">en Meta Ads</div>
            </div>
          </div>

          {/* Recommended Price */}
          <div className="bg-radar-accent/10 border border-radar-accent/30 rounded-lg p-4">
            <div className="text-xs text-radar-accent mb-1 flex items-center gap-1">
              <DollarSign className="w-3 h-3" /> Precio Recomendado
            </div>
            <div className="text-2xl font-bold text-radar-accent">
              ${product.recommendedPrice.toLocaleString()}
            </div>
            <div className="text-xs text-gray-400">Precio promedio mercado: ${product.avgPrice.toLocaleString()}</div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <button className="flex-1 bg-radar-card border border-radar-border rounded-lg p-3 flex items-center justify-center gap-2 hover:border-radar-accent/50 transition-colors">
              <Play className="w-4 h-4 text-radar-accent" />
              <span className="text-sm">Ver Creativos</span>
            </button>
            <button className="flex-1 bg-radar-card border border-radar-border rounded-lg p-3 flex items-center justify-center gap-2 hover:border-radar-accent/50 transition-colors">
              <Download className="w-4 h-4 text-radar-accent" />
              <span className="text-sm">Exportar</span>
            </button>
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
            <a href="#premium" className="text-gray-400 hover:text-radar-accent transition-colors flex items-center gap-2">
              <Eye className="w-4 h-4" />
              Ver Premium
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
            href="#premium"
            className="inline-flex items-center justify-center gap-2 bg-radar-card border border-radar-border text-white px-6 py-3 rounded-lg hover:border-radar-accent/50 transition-colors"
          >
            <Eye className="w-5 h-5" />
            Ver Análisis Premium
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
      </div>
    </section>
  )
}

function PremiumPreviewSection() {
  return (
    <section id="premium" className="py-16 px-4 border-t border-radar-border bg-gradient-to-b from-transparent to-radar-accent/5">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 bg-radar-accent/10 border border-radar-accent/30 text-radar-accent px-4 py-2 rounded-full text-sm font-medium mb-4">
            <Unlock className="w-4 h-4" />
            Así se ve con acceso completo
          </div>
          <h2 className="text-2xl md:text-3xl font-bold mb-4">
            Análisis <span className="gradient-text">Premium</span> Desbloqueado
          </h2>
          <p className="text-gray-400 max-w-2xl mx-auto">
            Esto es lo que ven los miembros de la comunidad. Análisis completo con IA, ángulos de venta probados, 
            triggers emocionales y precio recomendado.
          </p>
        </div>

        <PremiumProductCard />

        {/* CTA */}
        <div className="mt-12 text-center">
          <div className="bg-radar-card border border-radar-accent/30 rounded-xl p-8 max-w-2xl mx-auto">
            <Sparkles className="w-12 h-12 text-radar-accent mx-auto mb-4" />
            <h3 className="text-xl font-bold mb-2">¿Quieres acceso a todo esto?</h3>
            <p className="text-gray-400 mb-6">
              Únete a la comunidad de Trucos Ecomm & Drop y desbloquea análisis completos, creativos descargables y mucho más.
            </p>
            <a
              href="https://wa.me/34614696857?text=Hola%20Andrés%2C%20vi%20el%20análisis%20premium%20en%20Estrategas%20IA%20Tools%20y%20quiero%20ser%20parte%20de%20la%20comunidad"
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
      <PremiumPreviewSection />
      <Footer />
    </main>
  )
}
