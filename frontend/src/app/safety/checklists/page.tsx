'use client'

import React, { useEffect, useState, useCallback } from 'react'
import { useAuth, useRole, withAuth } from '@/components/auth/AuthProvider'
import { apiClient, SafetyChecklist } from '@/lib/api'
import { 
  Shield, 
  Plus, 
  Search, 
  Filter, 
  Eye, 
  Edit, 
  Trash2, 
  CheckCircle, 
  AlertTriangle, 
  Clock,
  Download
} from 'lucide-react'
import Link from 'next/link'

function SafetyChecklistsPage() {
  const { user } = useAuth()
  const { canViewAllChecklists } = useRole()
  const [checklists, setChecklists] = useState<SafetyChecklist[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  const loadChecklists = useCallback(async () => {
    try {
      setIsLoading(true)
      const params: any = {
        page: 1,
        per_page: 50
      }
      
      if (searchTerm) {
        params.project_name = searchTerm
      }
      
      if (statusFilter) {
        params.status = statusFilter
      }

      const response = await apiClient.getSafetyChecklists(params)
      setChecklists(response.items)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load checklists')
    } finally {
      setIsLoading(false)
    }
  }, [searchTerm, statusFilter])

  useEffect(() => {
    loadChecklists()
  }, [loadChecklists])

  const handleDelete = async (checklistId: string) => {
    if (!confirm('Are you sure you want to delete this checklist?')) {
      return
    }

    try {
      await apiClient.deleteSafetyChecklist(checklistId)
      await loadChecklists()
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete checklist')
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return 'bg-green-100 text-green-800'
      case 'completed':
        return 'bg-blue-100 text-blue-800'
      case 'draft':
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center">
                <Shield className="w-8 h-8 text-blue-600 mr-3" />
                Safety Checklists
              </h1>
              <p className="text-gray-600 mt-1">
                OSHA-compliant scaffolding safety inspections
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
        <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="relative">
              <Search className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search by project name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div className="relative">
              <Filter className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none"
              >
                <option value="">All Statuses</option>
                <option value="draft">Draft</option>
                <option value="completed">Completed</option>
                <option value="approved">Approved</option>
              </select>
            </div>

            <button
              onClick={() => {
                setSearchTerm('')
                setStatusFilter('')
              }}
              className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Clear Filters
            </button>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center">
              <AlertTriangle className="w-5 h-5 text-red-500 mr-2" />
              <p className="text-red-800">{error}</p>
            </div>
          </div>
        )}

        {checklists.length > 0 ? (
          <div className="grid gap-6">
            {checklists.map((checklist) => (
              <div key={checklist.id} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <div className="p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex-1">
                      <div className="flex items-center mb-2">
                        <h3 className="text-xl font-semibold text-gray-900 mr-3">
                          {checklist.project_name}
                        </h3>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium capitalize ${getStatusColor(checklist.status)}`}>
                          {checklist.status}
                        </span>
                        {checklist.critical_failures > 0 && (
                          <span className="ml-2 px-2 py-1 bg-red-100 text-red-800 text-xs font-bold rounded-full">
                            {checklist.critical_failures} Critical
                          </span>
                        )}
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm text-gray-600">
                        <div>
                          <span className="font-medium">Location:</span> {checklist.location}
                        </div>
                        <div>
                          <span className="font-medium">Scaffold Type:</span> {checklist.scaffold_type}
                        </div>
                        <div>
                          <span className="font-medium">Height:</span> {checklist.height}
                        </div>
                        <div>
                          <span className="font-medium">Date:</span> {new Date(checklist.inspection_date).toLocaleDateString()}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2 ml-4">
                      <Link
                        href={`/safety/checklist/${checklist.id}`}
                        className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        title="View Checklist"
                      >
                        <Eye className="w-5 h-5" />
                      </Link>
                      
                      {(checklist.inspector_id === user?.id || canViewAllChecklists) && checklist.status === 'draft' && (
                        <Link
                          href={`/safety/checklist/${checklist.id}/edit`}
                          className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                          title="Edit Checklist"
                        >
                          <Edit className="w-5 h-5" />
                        </Link>
                      )}

                      {(checklist.inspector_id === user?.id || canViewAllChecklists) && (
                        <button
                          onClick={() => handleDelete(checklist.id)}
                          className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                          title="Delete Checklist"
                        >
                          <Trash2 className="w-5 h-5" />
                        </button>
                      )}
                    </div>
                  </div>

                  <div className="mt-4">
                    <div className="flex justify-between text-sm text-gray-600 mb-2">
                      <span>Progress</span>
                      <span>{checklist.passed_items + checklist.failed_items + checklist.na_items} of {checklist.total_items}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{
                          width: `${((checklist.passed_items + checklist.failed_items + checklist.na_items) / checklist.total_items) * 100}%`
                        }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-sm p-12 text-center">
            <Shield className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No Safety Checklists Found</h3>
            <p className="text-gray-600 mb-6">
              Get started by creating your first OSHA safety checklist.
            </p>
            <Link
              href="/safety/checklist/new"
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 inline-flex items-center"
            >
              <Plus className="w-5 h-5 mr-2" />
              Create First Checklist
            </Link>
          </div>
        )}
      </div>
    </div>
  )
}

export default withAuth(SafetyChecklistsPage)
