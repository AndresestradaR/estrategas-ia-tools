# 🚀 Estrategas IA Tools

Product Research + Creativos + Análisis IA para Dropshipping LATAM.

![Estrategas IA Tools](https://via.placeholder.com/1200x630/0a0f1a/00ff88?text=Estrategas+IA+Tools)

## 🎯 ¿Qué es?

Una herramienta SaaS que combina:
- **DropKiller API** → Productos con ventas reales verificadas
- **Adskiller API** → Creativos de Meta/TikTok con análisis IA
- **Modelo Freemium** → Gratis limitado → WhatsApp → Comunidad Skool

## 🌟 Features

### Gratis (Todos)
- ✅ Ver Top productos del día
- ✅ Ventas 7d y 30d
- ✅ Stock disponible
- ✅ Score de oportunidad (sin explicación)

### Comunidad (Premium)
- 🔓 Análisis completo del score
- 🔓 Ángulos de venta probados
- 🔓 Creativos descargables
- 🔓 Target demográfico
- 🔓 Filtros avanzados
- 🔓 Sin límite de búsquedas

## 🛠️ Tech Stack

- **Frontend**: Next.js 14 + Tailwind CSS
- **Auth/DB**: Supabase
- **Hosting**: Vercel
- **APIs**: DropKiller + Adskiller

## 📦 Setup Local

```bash
# Clonar
git clone https://github.com/AndresestradaR/estrategas-ia-tools.git
cd estrategas-ia-tools

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env.local
# Editar .env.local con tus credenciales

# Correr en desarrollo
npm run dev
```

## 🚀 Deploy en Vercel

### Desde Claude Code:

```bash
# Clonar el repo
git clone https://github.com/AndresestradaR/estrategas-ia-tools.git
cd estrategas-ia-tools

# Login a Vercel (si no lo has hecho)
vercel login

# Deploy
vercel
```

### Variables de Entorno en Vercel:

```
NEXT_PUBLIC_SUPABASE_URL=tu_url_de_supabase
NEXT_PUBLIC_SUPABASE_ANON_KEY=tu_anon_key
NEXT_PUBLIC_WHATSAPP_NUMBER=34614696857
```

## 🗄️ Setup Supabase

1. Crear proyecto en [supabase.com](https://supabase.com)
2. Ir a SQL Editor y ejecutar:

```sql
-- Tabla de usuarios
CREATE TABLE users (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_login TIMESTAMP WITH TIME ZONE,
  is_community BOOLEAN DEFAULT FALSE
);

-- Tabla de búsquedas (analytics)
CREATE TABLE searches (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  query TEXT,
  product_id TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Habilitar Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE searches ENABLE ROW LEVEL SECURITY;
```

3. Copiar las credenciales a las variables de entorno

## 📁 Estructura del Proyecto

```
estrategas-ia-tools/
├── src/
│   ├── app/
│   │   ├── layout.tsx      # Layout principal
│   │   ├── page.tsx        # Página home
│   │   └── globals.css     # Estilos globales
│   ├── components/         # Componentes reutilizables
│   └── lib/
│       └── supabase.ts     # Config Supabase
├── package.json
├── tailwind.config.js
└── next.config.js
```

## 🔗 APIs Documentadas

Ver documentación completa en:
- [product-intelligence-dropi/docs/API_ENDPOINTS.md](https://github.com/AndresestradaR/product-intelligence-dropi/blob/main/docs/API_ENDPOINTS.md)

## 📞 Contacto

- **WhatsApp**: +34 614 696 857
- **Comunidad**: Trucos Ecomm & Drop (Skool)

---

Made with 💚 by Trucos Ecomm & Drop
