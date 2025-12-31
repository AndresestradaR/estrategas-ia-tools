import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Estrategas IA Tools | Product Research para Dropshipping',
  description: 'Encuentra productos ganadores, analiza creativos y descubre ángulos de venta con inteligencia artificial. La herramienta definitiva para dropshippers en LATAM.',
  keywords: ['dropshipping', 'product research', 'dropi', 'ecommerce', 'colombia', 'latinoamerica'],
  authors: [{ name: 'Trucos Ecomm & Drop' }],
  openGraph: {
    title: 'Estrategas IA Tools',
    description: 'Product Research con IA para Dropshipping LATAM',
    type: 'website',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es">
      <body className="min-h-screen bg-radar-dark antialiased">
        <div className="grid-pattern fixed inset-0 pointer-events-none opacity-50" />
        <div className="relative z-10">
          {children}
        </div>
      </body>
    </html>
  )
}
