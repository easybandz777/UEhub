'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Button } from '../components/ui/button'
import { 
  Package, 
  Shield, 
  BarChart3, 
  Webhook, 
  ArrowRight,
  CheckCircle,
  Users,
  TrendingUp,
  AlertTriangle,
  FileCheck
} from 'lucide-react'

export default function HomePage() {
  const [isLoaded, setIsLoaded] = useState(false)

  useEffect(() => {
    setIsLoaded(true)
  }, [])

  const features = [
    {
      icon: Package,
      title: 'Inventory Management',
      description: 'Track items, quantities, locations, and movements with real-time updates and low-stock alerts.',
      href: '/inventory',
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      icon: Shield,
      title: 'OSHA Safety Checklist',
      description: 'Comprehensive scaffolding safety inspections based on OSHA 29 CFR 1926.451-454 standards.',
      href: '/safety',
      color: 'text-red-600',
      bgColor: 'bg-red-50',
    },
    {
      icon: BarChart3,
      title: 'Analytics & Reports',
      description: 'Comprehensive reporting with charts, KPIs, and compliance tracking.',
      href: '/reports',
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      icon: Webhook,
      title: 'Webhooks & Integration',
      description: 'Connect with external systems through secure webhooks and APIs.',
      href: '/webhooks',
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
    },
  ]

  const stats = [
    { label: 'Active Users', value: '150+', icon: Users },
    { label: 'Inventory Items', value: '2.5K+', icon: Package },
    { label: 'Safety Inspections', value: '500+', icon: Shield },
    { label: 'Compliance Rate', value: '98%', icon: TrendingUp },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Hero Section */}
      <section className="relative overflow-hidden py-20 sm:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className={`text-center transition-all duration-1000 ${
            isLoaded ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
          }`}>
            <h1 className="text-4xl sm:text-6xl font-bold text-gray-900 mb-6">
              <span className="block">Welcome to</span>
              <span className="block bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Upper Echelon Hub
              </span>
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto text-balance">
              Your comprehensive platform for inventory management and OSHA safety compliance.
              Everything you need to keep your operations running safely and efficiently.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/inventory">
                <Button size="lg" className="group bg-blue-600 hover:bg-blue-700">
                  Manage Inventory
                  <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                </Button>
              </Link>
              <Link href="/safety">
                <Button variant="outline" size="lg" className="border-red-600 text-red-600 hover:bg-red-600 hover:text-white">
                  Safety Checklist
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div 
                key={stat.label}
                className={`text-center transition-all duration-700 delay-${index * 100} ${
                  isLoaded ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
                }`}
              >
                <div className="flex justify-center mb-4">
                  <stat.icon className="h-8 w-8 text-blue-600" />
                </div>
                <div className="text-3xl font-bold text-gray-900 mb-2">
                  {stat.value}
                </div>
                <div className="text-gray-600">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Powerful Features
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Everything you need to manage inventory and ensure safety compliance in one integrated platform.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {features.map((feature, index) => (
              <div
                key={feature.title}
                className={`group bg-white rounded-xl p-8 shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-1 ${
                  isLoaded ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
                }`}
                style={{ transitionDelay: `${index * 150}ms` }}
              >
                <div className={`inline-flex items-center justify-center w-12 h-12 rounded-lg ${feature.bgColor} mb-6`}>
                  <feature.icon className={`h-6 w-6 ${feature.color}`} />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600 mb-6">
                  {feature.description}
                </p>
                <Link href={feature.href}>
                  <Button variant="ghost" className="group-hover:translate-x-1 transition-transform">
                    Learn More
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Safety Highlight Section */}
      <section className="py-20 bg-gradient-to-r from-red-600 to-red-700 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="flex items-center mb-6">
                <AlertTriangle className="h-8 w-8 mr-3" />
                <h2 className="text-3xl sm:text-4xl font-bold">
                  Safety First
                </h2>
              </div>
              <p className="text-xl text-red-100 mb-8">
                Our comprehensive OSHA scaffolding safety checklist ensures your worksite meets all regulatory requirements and keeps your team safe.
              </p>
              <div className="space-y-4">
                {[
                  'Based on OSHA 29 CFR 1926.451-454',
                  'Comprehensive 35+ point inspection',
                  'Critical safety item identification',
                  'Downloadable compliance reports',
                  'Real-time inspection tracking'
                ].map((item, index) => (
                  <div key={index} className="flex items-center">
                    <CheckCircle className="h-5 w-5 text-red-200 mr-3 flex-shrink-0" />
                    <span className="text-red-100">{item}</span>
                  </div>
                ))}
              </div>
              <div className="mt-8">
                <Link href="/safety">
                  <Button size="lg" variant="secondary" className="bg-white text-red-600 hover:bg-red-50">
                    Start Safety Inspection
                    <FileCheck className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
              </div>
            </div>
            <div className="relative">
              <div className="aspect-square bg-white/10 rounded-2xl p-8 backdrop-blur-sm">
                <div className="h-full flex flex-col justify-center items-center text-center">
                  <Shield className="h-24 w-24 mb-6 text-white/90" />
                  <h3 className="text-2xl font-bold mb-4">OSHA Compliant</h3>
                  <p className="text-red-100 text-lg">
                    Ensure full compliance with federal safety regulations and protect your workforce.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="relative">
              <div className="aspect-square bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl p-8 text-white">
                <div className="h-full flex flex-col justify-center items-center text-center">
                  <Package className="h-16 w-16 mb-4 opacity-90" />
                  <h3 className="text-2xl font-bold mb-2">Enterprise Ready</h3>
                  <p className="opacity-90">
                    Built for scale with enterprise-grade security and reliability.
                  </p>
                </div>
              </div>
            </div>
            <div>
              <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-6">
                Why Choose UE Hub?
              </h2>
              <div className="space-y-6">
                {[
                  'Modular architecture for easy customization',
                  'Real-time updates and notifications',
                  'Comprehensive audit trails and compliance',
                  'Scalable cloud infrastructure',
                  'Advanced security and access controls',
                  'Mobile-responsive design',
                ].map((benefit, index) => (
                  <div key={index} className="flex items-center">
                    <CheckCircle className="h-5 w-5 text-green-600 mr-3 flex-shrink-0" />
                    <span className="text-gray-700">{benefit}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">
            Ready to Get Started?
          </h2>
          <p className="text-xl text-white/90 mb-8">
            Join hundreds of organizations already using UE Hub to streamline their operations and ensure safety compliance.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/inventory">
              <Button size="lg" variant="secondary">
                Explore Inventory
              </Button>
            </Link>
            <Link href="/safety">
              <Button size="lg" variant="outline" className="text-white border-white hover:bg-white hover:text-blue-600">
                Try Safety Checklist
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center mb-4">
                <Shield className="h-6 w-6 mr-2" />
                <span className="text-lg font-semibold">UE Hub</span>
              </div>
              <p className="text-gray-400">
                Streamlining operations with intelligent inventory management and safety compliance tools.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Features</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/inventory" className="hover:text-white">Inventory Management</Link></li>
                <li><Link href="/safety" className="hover:text-white">OSHA Safety</Link></li>
                <li><Link href="/reports" className="hover:text-white">Reports</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Support</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/docs" className="hover:text-white">Documentation</Link></li>
                <li><Link href="/help" className="hover:text-white">Help Center</Link></li>
                <li><Link href="/contact" className="hover:text-white">Contact</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/about" className="hover:text-white">About</Link></li>
                <li><Link href="/privacy" className="hover:text-white">Privacy</Link></li>
                <li><Link href="/terms" className="hover:text-white">Terms</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 Upper Echelon Hub. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}