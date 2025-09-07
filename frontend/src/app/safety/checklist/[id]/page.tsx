'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useAuth, useRole, withAuth } from '@/components/auth/AuthProvider'
import { apiClient, SafetyChecklist } from '@/lib/api'
import { 
  Shield, 
  ArrowLeft, 
  Edit, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  Clock,
  User,
  Calendar,
  MapPin,
  Ruler,
  Building,
  FileText,
  Download,
  Check,
  X
} from 'lucide-react'
import Link from 'next/link'

function ChecklistViewPage() {
  const params = useParams()
  const router = useRouter()
  const { user } = useAuth()
  const { canApproveChecklists, canViewAllChecklists } = useRole()
  const [checklist, setChecklist] = useState<SafetyChecklist | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [isApproving, setIsApproving] = useState(false)
  const [approvalComments, setApprovalComments] = useState('')

  const checklistId = params.id as string

  const loadChecklist = useCallback(async () => {
    try {
      setIsLoading(true)
      const data = await apiClient.getSafetyChecklist(checklistId)
      setChecklist(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load checklist')
    } finally {
      setIsLoading(false)
    }
  }, [checklistId])

  useEffect(() => {
    if (checklistId) {
      loadChecklist()
    }
  }, [checklistId, loadChecklist])

  const handleApproval = async (approved: boolean) => {
    if (!checklist) return

    try {
      setIsApproving(true)
      await apiClient.approveChecklist(checklistId, approved, approvalComments)
      await loadChecklist()
      setApprovalComments('')
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to process approval')
    } finally {
      setIsApproving(false)
    }
  }

  const canEdit = checklist && (
    checklist.inspector_id === user?.id || canViewAllChecklists
  ) && checklist.status === 'draft'

  const canApprove = checklist && canApproveChecklists && checklist.status === 'completed'

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error || !checklist) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Checklist</h2>
          <p className="text-gray-600 mb-4">{error || 'Checklist not found'}</p>
          <Link
            href="/safety/checklists"
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            Back to Checklists
          </Link>
        </div>
      </div>
    )
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

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved':
        return <CheckCircle className="w-5 h-5" />
      case 'completed':
        return <Clock className="w-5 h-5" />
      case 'draft':
        return <Edit className="w-5 h-5" />
      default:
        return <AlertTriangle className="w-5 h-5" />
    }
  }

  const categories = Array.from(new Set(checklist.checklist_items.map(item => item.category)))

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Link
                href="/safety/checklists"
                className="mr-4 p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg"
              >
                <ArrowLeft className="w-5 h-5" />
              </Link>
              <div>
                <div className="flex items-center mb-2">
                  <Shield className="w-8 h-8 text-blue-600 mr-3" />
                  <h1 className="text-3xl font-bold text-gray-900">{checklist.project_name}</h1>
                  <span className={`ml-4 px-3 py-1 rounded-full text-sm font-medium flex items-center ${getStatusColor(checklist.status)}`}>
                    {getStatusIcon(checklist.status)}
                    <span className="ml-1 capitalize">{checklist.status}</span>
                  </span>
                  {checklist.critical_failures > 0 && (
                    <span className="ml-2 px-2 py-1 bg-red-100 text-red-800 text-xs font-bold rounded-full">
                      {checklist.critical_failures} Critical Failures
                    </span>
                  )}
                </div>
                <p className="text-gray-600">
                  OSHA Scaffolding Safety Inspection - {checklist.location}
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              {canEdit && (
                <Link
                  href={`/safety/checklist/${checklistId}/edit`}
                  className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center"
                >
                  <Edit className="w-5 h-5 mr-2" />
                  Edit
                </Link>
              )}
              
              <button
                onClick={() => {
                  // TODO: Implement report generation
                  alert('Report generation coming soon!')
                }}
                className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 flex items-center"
              >
                <Download className="w-5 h-5 mr-2" />
                Export
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-4 gap-8">
          {/* Sidebar - Project Info & Stats */}
          <div className="lg:col-span-1">
            <div className="space-y-6">
              {/* Project Information */}
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Project Information</h3>
                
                <div className="space-y-3 text-sm">
                  <div className="flex items-center">
                    <MapPin className="w-4 h-4 text-gray-500 mr-2" />
                    <span className="text-gray-600">Location:</span>
                    <span className="ml-2 font-medium">{checklist.location}</span>
                  </div>
                  
                  <div className="flex items-center">
                    <Calendar className="w-4 h-4 text-gray-500 mr-2" />
                    <span className="text-gray-600">Date:</span>
                    <span className="ml-2 font-medium">{new Date(checklist.inspection_date).toLocaleDateString()}</span>
                  </div>
                  
                  <div className="flex items-center">
                    <Building className="w-4 h-4 text-gray-500 mr-2" />
                    <span className="text-gray-600">Scaffold Type:</span>
                    <span className="ml-2 font-medium">{checklist.scaffold_type}</span>
                  </div>
                  
                  <div className="flex items-center">
                    <Ruler className="w-4 h-4 text-gray-500 mr-2" />
                    <span className="text-gray-600">Height:</span>
                    <span className="ml-2 font-medium">{checklist.height}</span>
                  </div>
                  
                  {checklist.contractor && (
                    <div className="flex items-center">
                      <User className="w-4 h-4 text-gray-500 mr-2" />
                      <span className="text-gray-600">Contractor:</span>
                      <span className="ml-2 font-medium">{checklist.contractor}</span>
                    </div>
                  )}
                  
                  {checklist.permit_number && (
                    <div className="flex items-center">
                      <FileText className="w-4 h-4 text-gray-500 mr-2" />
                      <span className="text-gray-600">Permit:</span>
                      <span className="ml-2 font-medium">{checklist.permit_number}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Progress Stats */}
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Inspection Progress</h3>
                
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm text-gray-600 mb-2">
                      <span>Completion</span>
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
                  
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="bg-green-50 rounded-lg p-3">
                      <div className="text-green-800 font-bold text-lg">{checklist.passed_items}</div>
                      <div className="text-green-600">Passed</div>
                    </div>
                    
                    <div className="bg-red-50 rounded-lg p-3">
                      <div className="text-red-800 font-bold text-lg">{checklist.failed_items}</div>
                      <div className="text-red-600">Failed</div>
                    </div>
                    
                    <div className="bg-gray-50 rounded-lg p-3">
                      <div className="text-gray-800 font-bold text-lg">{checklist.na_items}</div>
                      <div className="text-gray-600">N/A</div>
                    </div>
                    
                    <div className="bg-yellow-50 rounded-lg p-3">
                      <div className="text-yellow-800 font-bold text-lg">
                        {checklist.total_items - checklist.passed_items - checklist.failed_items - checklist.na_items}
                      </div>
                      <div className="text-yellow-600">Pending</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Approval Section */}
              {canApprove && (
                <div className="bg-white rounded-xl shadow-sm p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Approval</h3>
                  
                  <div className="space-y-4">
                    <textarea
                      value={approvalComments}
                      onChange={(e) => setApprovalComments(e.target.value)}
                      placeholder="Add approval comments (optional)..."
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                      rows={3}
                    />
                    
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleApproval(true)}
                        disabled={isApproving}
                        className="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center justify-center"
                      >
                        <Check className="w-4 h-4 mr-2" />
                        Approve
                      </button>
                      
                      <button
                        onClick={() => handleApproval(false)}
                        disabled={isApproving}
                        className="flex-1 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 disabled:opacity-50 flex items-center justify-center"
                      >
                        <X className="w-4 h-4 mr-2" />
                        Reject
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Main Content - Checklist Items */}
          <div className="lg:col-span-3">
            <div className="space-y-6">
              {categories.map((category) => {
                const categoryItems = checklist.checklist_items.filter(item => item.category === category)
                
                return (
                  <div key={category} className="bg-white rounded-xl shadow-sm">
                    <div className="bg-gradient-to-r from-slate-600 to-slate-700 text-white px-6 py-4 rounded-t-xl">
                      <h3 className="text-xl font-bold">{category}</h3>
                      <p className="text-slate-200 text-sm">{categoryItems.length} items</p>
                    </div>
                    
                    <div className="p-6 space-y-4">
                      {categoryItems.map((item) => (
                        <div
                          key={item.id}
                          className={`border-l-4 ${
                            item.status === 'pass' ? 'border-green-500 bg-green-50' :
                            item.status === 'fail' ? 'border-red-500 bg-red-50' :
                            item.status === 'na' ? 'border-gray-400 bg-gray-50' :
                            'border-gray-200 bg-white'
                          } rounded-r-lg p-4`}
                        >
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex-1">
                              <div className="flex items-center mb-2">
                                <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-semibold mr-3">
                                  {item.number}
                                </span>
                                {item.is_critical && (
                                  <span className="bg-red-100 text-red-800 px-2 py-1 rounded text-xs font-bold mr-2">
                                    CRITICAL
                                  </span>
                                )}
                                {item.status && (
                                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                                    item.status === 'pass' ? 'bg-green-100 text-green-800' :
                                    item.status === 'fail' ? 'bg-red-100 text-red-800' :
                                    'bg-gray-100 text-gray-800'
                                  }`}>
                                    {item.status === 'pass' ? 'PASS' : item.status === 'fail' ? 'FAIL' : 'N/A'}
                                  </span>
                                )}
                              </div>
                              <p className="text-gray-800 leading-relaxed mb-2">{item.text}</p>
                              {item.notes && (
                                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mt-2">
                                  <p className="text-sm text-blue-800">
                                    <strong>Notes:</strong> {item.notes}
                                  </p>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default withAuth(ChecklistViewPage)
