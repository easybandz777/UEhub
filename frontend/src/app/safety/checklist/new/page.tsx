'use client'

import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth, withAuth } from '@/components/auth/AuthProvider'
import { apiClient, SafetyChecklistCreate } from '@/lib/api'
import { Shield, Save, ArrowLeft, AlertTriangle } from 'lucide-react'
import Link from 'next/link'

interface ChecklistItem {
  item_id: string
  category: string
  number: string
  text: string
  is_critical: boolean
  status?: 'pass' | 'fail' | 'na'
  notes?: string
}

function NewChecklistPage() {
  const router = useRouter()
  const { user } = useAuth()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [template, setTemplate] = useState<any>(null)
  
  const [formData, setFormData] = useState({
    project_name: '',
    location: '',
    inspection_date: new Date().toISOString().split('T')[0],
    scaffold_type: '',
    height: '',
    contractor: '',
    permit_number: ''
  })

  const [checklistItems, setChecklistItems] = useState<ChecklistItem[]>([])

  useEffect(() => {
    loadTemplate()
  }, [])

  const loadTemplate = async () => {
    try {
      const templateData = await apiClient.getDefaultOSHATemplate()
      setTemplate(templateData)
      
      // Convert template to checklist items
      const items: ChecklistItem[] = []
      templateData.template_data.categories.forEach((category: any) => {
        category.items.forEach((item: any) => {
          items.push({
            item_id: item.id,
            category: category.name,
            number: item.number,
            text: item.text,
            is_critical: item.critical,
            status: undefined,
            notes: ''
          })
        })
      })
      setChecklistItems(items)
    } catch (err) {
      setError('Failed to load checklist template')
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
  }

  const handleItemUpdate = (itemId: string, field: 'status' | 'notes', value: string) => {
    setChecklistItems(prev => 
      prev.map(item => 
        item.item_id === itemId 
          ? { ...item, [field]: value }
          : item
      )
    )
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      const checklistData: SafetyChecklistCreate = {
        ...formData,
        checklist_items: checklistItems
      }

      const newChecklist = await apiClient.createSafetyChecklist(checklistData)
      router.push(`/safety/checklist/${newChecklist.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create checklist')
    } finally {
      setIsLoading(false)
    }
  }

  const getCompletionStats = () => {
    const total = checklistItems.length
    const completed = checklistItems.filter(item => item.status).length
    const passed = checklistItems.filter(item => item.status === 'pass').length
    const failed = checklistItems.filter(item => item.status === 'fail').length
    const na = checklistItems.filter(item => item.status === 'na').length
    const criticalFailed = checklistItems.filter(item => item.is_critical && item.status === 'fail').length

    return { total, completed, passed, failed, na, criticalFailed }
  }

  const stats = getCompletionStats()
  const categories = Array.from(new Set(checklistItems.map(item => item.category)))

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
                <h1 className="text-3xl font-bold text-gray-900 flex items-center">
                  <Shield className="w-8 h-8 text-blue-600 mr-3" />
                  New Safety Checklist
                </h1>
                <p className="text-gray-600 mt-1">
                  OSHA Scaffolding Safety Inspection - 29 CFR 1926.451-454
                </p>
              </div>
            </div>
            
            <button
              onClick={handleSubmit}
              disabled={isLoading}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center"
            >
              {isLoading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              ) : (
                <Save className="w-5 h-5 mr-2" />
              )}
              Save Checklist
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center">
              <AlertTriangle className="w-5 h-5 text-red-500 mr-2" />
              <p className="text-red-800">{error}</p>
            </div>
          </div>
        )}

        <div className="grid lg:grid-cols-4 gap-8">
          {/* Sidebar - Project Info */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-sm p-6 sticky top-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Project Information</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Project Name *
                  </label>
                  <input
                    type="text"
                    name="project_name"
                    value={formData.project_name}
                    onChange={handleInputChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Enter project name"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Location *
                  </label>
                  <input
                    type="text"
                    name="location"
                    value={formData.location}
                    onChange={handleInputChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Enter location"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Inspection Date *
                  </label>
                  <input
                    type="date"
                    name="inspection_date"
                    value={formData.inspection_date}
                    onChange={handleInputChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Scaffold Type *
                  </label>
                  <input
                    type="text"
                    name="scaffold_type"
                    value={formData.scaffold_type}
                    onChange={handleInputChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., Frame, Tube & Clamp"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Height *
                  </label>
                  <input
                    type="text"
                    name="height"
                    value={formData.height}
                    onChange={handleInputChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., 20 ft"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Contractor
                  </label>
                  <input
                    type="text"
                    name="contractor"
                    value={formData.contractor}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Enter contractor name"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Permit Number
                  </label>
                  <input
                    type="text"
                    name="permit_number"
                    value={formData.permit_number}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Enter permit number"
                  />
                </div>
              </div>

              {/* Progress Stats */}
              <div className="mt-6 pt-6 border-t border-gray-200">
                <h4 className="text-sm font-medium text-gray-900 mb-3">Progress</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Completed:</span>
                    <span className="font-medium">{stats.completed}/{stats.total}</span>
                  </div>
                  <div className="flex justify-between text-green-600">
                    <span>Passed:</span>
                    <span className="font-medium">{stats.passed}</span>
                  </div>
                  <div className="flex justify-between text-red-600">
                    <span>Failed:</span>
                    <span className="font-medium">{stats.failed}</span>
                  </div>
                  <div className="flex justify-between text-gray-600">
                    <span>N/A:</span>
                    <span className="font-medium">{stats.na}</span>
                  </div>
                  {stats.criticalFailed > 0 && (
                    <div className="flex justify-between text-red-800 font-bold">
                      <span>Critical Failures:</span>
                      <span>{stats.criticalFailed}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Main Content - Checklist Items */}
          <div className="lg:col-span-3">
            <div className="space-y-6">
              {categories.map((category) => {
                const categoryItems = checklistItems.filter(item => item.category === category)
                
                return (
                  <div key={category} className="bg-white rounded-xl shadow-sm">
                    <div className="bg-gradient-to-r from-slate-600 to-slate-700 text-white px-6 py-4 rounded-t-xl">
                      <h3 className="text-xl font-bold">{category}</h3>
                      <p className="text-slate-200 text-sm">{categoryItems.length} items</p>
                    </div>
                    
                    <div className="p-6 space-y-4">
                      {categoryItems.map((item) => (
                        <div
                          key={item.item_id}
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
                              </div>
                              <p className="text-gray-800 leading-relaxed">{item.text}</p>
                            </div>
                          </div>
                          
                          <div className="flex flex-wrap gap-3 mb-3">
                            {['pass', 'fail', 'na'].map((status) => (
                              <button
                                key={status}
                                onClick={() => handleItemUpdate(item.item_id, 'status', status)}
                                className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                                  item.status === status 
                                    ? status === 'pass' ? 'bg-green-500 text-white' :
                                      status === 'fail' ? 'bg-red-500 text-white' :
                                      'bg-gray-500 text-white'
                                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                                }`}
                              >
                                {status === 'pass' ? 'Pass' : status === 'fail' ? 'Fail' : 'N/A'}
                              </button>
                            ))}
                          </div>
                          
                          <textarea
                            value={item.notes || ''}
                            onChange={(e) => handleItemUpdate(item.item_id, 'notes', e.target.value)}
                            placeholder="Add notes, observations, or corrective actions..."
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                            rows={2}
                          />
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

export default withAuth(NewChecklistPage)
