'use client'

import React, { useEffect, useState } from 'react'
import { useAuth, useRole, withAuth } from '@/components/auth/AuthProvider'
import { apiClient, SafetyStats, SafetyChecklist } from '@/lib/api'
import { 
  Shield, 
  CheckCircle, 
  AlertTriangle, 
  Clock, 
  Users, 
  TrendingUp,
  Plus,
  Eye,
  FileText
} from 'lucide-react'
import Link from 'next/link'

interface DashboardData {
  stats: SafetyStats
  recent_checklists: SafetyChecklist[]
  pending_approvals: SafetyChecklist[]
  critical_failures: SafetyChecklist[]
}

function DashboardPage() {
  const { user } = useAuth()
  const { role, canApproveChecklists, canViewAllChecklists } = useRole()
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setIsLoading(true)
      const data = await apiClient.getSafetyDashboard()
      setDashboardData(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard')
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Dashboard</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={loadDashboardData}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  const stats = dashboardData?.stats

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
              <p className="text-gray-600 mt-1">
                Welcome back, {user?.name} ({role})
              </p>
            </div>
            <Link
              href="/safety/checklist/new"
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center"
            >
              <Plus className="w-5 h-5 mr-2" />
              New Checklist
            </Link>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center">
              <div className="bg-blue-100 rounded-lg p-3 mr-4">
                <FileText className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Total Checklists</p>
                <p className="text-2xl font-bold text-gray-900">{stats?.total_checklists || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center">
              <div className="bg-green-100 rounded-lg p-3 mr-4">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Completed</p>
                <p className="text-2xl font-bold text-gray-900">{stats?.completed_checklists || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center">
              <div className="bg-orange-100 rounded-lg p-3 mr-4">
                <Clock className="w-6 h-6 text-orange-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Pending Approval</p>
                <p className="text-2xl font-bold text-gray-900">{stats?.pending_approval || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center">
              <div className="bg-red-100 rounded-lg p-3 mr-4">
                <AlertTriangle className="w-6 h-6 text-red-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Critical Failures</p>
                <p className="text-2xl font-bold text-gray-900">{stats?.critical_failures_count || 0}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Additional Stats Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Completion Rate</h3>
              <TrendingUp className="w-5 h-5 text-green-500" />
            </div>
            <div className="text-3xl font-bold text-green-600 mb-2">
              {stats?.average_completion_rate || 0}%
            </div>
            <p className="text-sm text-gray-600">Average across all checklists</p>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">This Month</h3>
              <Shield className="w-5 h-5 text-blue-500" />
            </div>
            <div className="text-3xl font-bold text-blue-600 mb-2">
              {stats?.checklists_this_month || 0}
            </div>
            <p className="text-sm text-gray-600">Checklists created</p>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">This Week</h3>
              <Users className="w-5 h-5 text-purple-500" />
            </div>
            <div className="text-3xl font-bold text-purple-600 mb-2">
              {stats?.checklists_this_week || 0}
            </div>
            <p className="text-sm text-gray-600">Recent activity</p>
          </div>
        </div>

        {/* Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Checklists */}
          <div className="bg-white rounded-xl shadow-sm">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold text-gray-900">Recent Checklists</h3>
                <Link
                  href="/safety/checklists"
                  className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                >
                  View All
                </Link>
              </div>
            </div>
            <div className="p-6">
              {dashboardData?.recent_checklists?.length ? (
                <div className="space-y-4">
                  {dashboardData.recent_checklists.slice(0, 5).map((checklist) => (
                    <div key={checklist.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div>
                        <h4 className="font-medium text-gray-900">{checklist.project_name}</h4>
                        <p className="text-sm text-gray-600">{checklist.location}</p>
                        <p className="text-xs text-gray-500">
                          {new Date(checklist.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          checklist.status === 'approved' ? 'bg-green-100 text-green-800' :
                          checklist.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {checklist.status}
                        </span>
                        <Link
                          href={`/safety/checklist/${checklist.id}`}
                          className="text-blue-600 hover:text-blue-700"
                        >
                          <Eye className="w-4 h-4" />
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">No checklists yet</p>
                  <Link
                    href="/safety/checklist/new"
                    className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                  >
                    Create your first checklist
                  </Link>
                </div>
              )}
            </div>
          </div>

          {/* Pending Approvals (Admin/Superadmin only) */}
          {canApproveChecklists && (
            <div className="bg-white rounded-xl shadow-sm">
              <div className="p-6 border-b border-gray-200">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-semibold text-gray-900">Pending Approvals</h3>
                  <Link
                    href="/safety/approvals"
                    className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                  >
                    View All
                  </Link>
                </div>
              </div>
              <div className="p-6">
                {dashboardData?.pending_approvals?.length ? (
                  <div className="space-y-4">
                    {dashboardData.pending_approvals.slice(0, 5).map((checklist) => (
                      <div key={checklist.id} className="flex items-center justify-between p-4 bg-orange-50 rounded-lg">
                        <div>
                          <h4 className="font-medium text-gray-900">{checklist.project_name}</h4>
                          <p className="text-sm text-gray-600">{checklist.location}</p>
                          <p className="text-xs text-gray-500">
                            Completed {new Date(checklist.updated_at).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="px-2 py-1 text-xs rounded-full bg-orange-100 text-orange-800">
                            Needs Review
                          </span>
                          <Link
                            href={`/safety/checklist/${checklist.id}`}
                            className="text-blue-600 hover:text-blue-700"
                          >
                            <Eye className="w-4 h-4" />
                          </Link>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Clock className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">No pending approvals</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Critical Failures */}
          {!canApproveChecklists && dashboardData?.critical_failures?.length ? (
            <div className="bg-white rounded-xl shadow-sm">
              <div className="p-6 border-b border-gray-200">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-semibold text-gray-900">Critical Failures</h3>
                  <Link
                    href="/safety/checklists?critical_failures_only=true"
                    className="text-red-600 hover:text-red-700 text-sm font-medium"
                  >
                    View All
                  </Link>
                </div>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  {dashboardData.critical_failures.slice(0, 5).map((checklist) => (
                    <div key={checklist.id} className="flex items-center justify-between p-4 bg-red-50 rounded-lg">
                      <div>
                        <h4 className="font-medium text-gray-900">{checklist.project_name}</h4>
                        <p className="text-sm text-gray-600">{checklist.location}</p>
                        <p className="text-xs text-red-600 font-medium">
                          {checklist.critical_failures} critical failure{checklist.critical_failures !== 1 ? 's' : ''}
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="px-2 py-1 text-xs rounded-full bg-red-100 text-red-800">
                          Critical
                        </span>
                        <Link
                          href={`/safety/checklist/${checklist.id}`}
                          className="text-blue-600 hover:text-blue-700"
                        >
                          <Eye className="w-4 h-4" />
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="mt-8 bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link
              href="/safety/checklist/new"
              className="flex items-center p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
            >
              <Plus className="w-8 h-8 text-blue-600 mr-3" />
              <div>
                <h4 className="font-medium text-gray-900">New Safety Checklist</h4>
                <p className="text-sm text-gray-600">Start a new OSHA inspection</p>
              </div>
            </Link>

            <Link
              href="/safety/checklists"
              className="flex items-center p-4 border border-gray-200 rounded-lg hover:border-green-300 hover:bg-green-50 transition-colors"
            >
              <FileText className="w-8 h-8 text-green-600 mr-3" />
              <div>
                <h4 className="font-medium text-gray-900">View All Checklists</h4>
                <p className="text-sm text-gray-600">Browse and manage checklists</p>
              </div>
            </Link>

            <Link
              href="/inventory"
              className="flex items-center p-4 border border-gray-200 rounded-lg hover:border-purple-300 hover:bg-purple-50 transition-colors"
            >
              <Shield className="w-8 h-8 text-purple-600 mr-3" />
              <div>
                <h4 className="font-medium text-gray-900">Inventory Management</h4>
                <p className="text-sm text-gray-600">Manage equipment and supplies</p>
              </div>
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default withAuth(DashboardPage)
