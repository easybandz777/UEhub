'use client'

import React, { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/components/auth/AuthProvider'
import LoginForm from '@/components/auth/LoginForm'
import { Shield, CheckCircle, Users, BarChart3 } from 'lucide-react'

export default function LoginPage() {
  const { isAuthenticated, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push('/dashboard')
    }
  }, [isAuthenticated, isLoading, router])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (isAuthenticated) {
    return null // Will redirect
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-2 gap-12 items-center min-h-screen">
          {/* Left side - Branding and features */}
          <div className="space-y-8">
            <div>
              <h1 className="text-5xl font-bold text-gray-900 mb-4">
                UE Hub
              </h1>
              <p className="text-xl text-gray-600 mb-8">
                Professional safety management and inventory tracking for construction teams
              </p>
            </div>

            <div className="grid gap-6">
              <div className="flex items-start space-x-4">
                <div className="bg-blue-100 rounded-lg p-3">
                  <Shield className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    OSHA Safety Compliance
                  </h3>
                  <p className="text-gray-600">
                    Comprehensive scaffolding safety checklists based on 29 CFR 1926.451-454 standards
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className="bg-green-100 rounded-lg p-3">
                  <CheckCircle className="w-6 h-6 text-green-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    Digital Inspections
                  </h3>
                  <p className="text-gray-600">
                    Replace paper checklists with digital forms that save time and ensure accuracy
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className="bg-purple-100 rounded-lg p-3">
                  <Users className="w-6 h-6 text-purple-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    Team Management
                  </h3>
                  <p className="text-gray-600">
                    Role-based access control with approval workflows for supervisors
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className="bg-orange-100 rounded-lg p-3">
                  <BarChart3 className="w-6 h-6 text-orange-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    Analytics & Reporting
                  </h3>
                  <p className="text-gray-600">
                    Track safety performance and generate compliance reports automatically
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-lg">
              <h4 className="text-lg font-semibold text-gray-900 mb-3">
                Getting Started
              </h4>
              <div className="space-y-2 text-sm text-gray-600">
                <p>• <strong>New users:</strong> Create an account to start as an Employee</p>
                <p>• <strong>Employees:</strong> Create and manage your own safety checklists</p>
                <p>• <strong>Admins:</strong> Approve checklists and manage templates</p>
                <p>• <strong>Superadmins:</strong> Full system access and user management</p>
              </div>
            </div>
          </div>

          {/* Right side - Login form */}
          <div className="flex items-center justify-center">
            <LoginForm />
          </div>
        </div>
      </div>
    </div>
  )
}
