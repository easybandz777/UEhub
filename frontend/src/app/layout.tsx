import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Navigation from '../components/Navigation'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'UE Hub - Upper Echelon Hub',
  description: 'Inventory management and OSHA safety training system',
  keywords: ['inventory', 'training', 'OSHA', 'safety', 'scaffolding', 'management'],
  authors: [{ name: 'UE Hub Team' }],
  viewport: 'width=device-width, initial-scale=1',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <div id="root">
          <Navigation />
          <main>
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}