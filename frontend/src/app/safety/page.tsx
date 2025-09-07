'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { CheckCircle, XCircle, AlertTriangle, FileText, Download, RotateCcw, Eye, EyeOff } from 'lucide-react'

interface ChecklistItem {
  id: string
  category: string
  number: string
  text: string
  status: 'pass' | 'fail' | 'na' | ''
  notes: string
  critical: boolean
}

interface ProjectInfo {
  projectName: string
  location: string
  inspector: string
  date: string
  scaffoldType: string
  height: string
  contractor: string
  permitNumber: string
}

const OSHAScaffoldingChecklist = () => {
  const [projectInfo, setProjectInfo] = useState<ProjectInfo>({
    projectName: '',
    location: '',
    inspector: '',
    date: new Date().toISOString().split('T')[0],
    scaffoldType: '',
    height: '',
    contractor: '',
    permitNumber: ''
  })

  const [checklistItems, setChecklistItems] = useState<ChecklistItem[]>([
    // Foundation & Support
    { id: '1.1', category: 'Foundation & Support', number: '1.1', text: 'Foundation is level, sound, rigid, and capable of supporting 4x intended load (minimum 25 psf)', status: '', notes: '', critical: true },
    { id: '1.2', category: 'Foundation & Support', number: '1.2', text: 'Base plates and mud sills properly installed under each leg', status: '', notes: '', critical: true },
    { id: '1.3', category: 'Foundation & Support', number: '1.3', text: 'Scaffold is plumb, level, and square within tolerance (±1/4 inch per 10 feet)', status: '', notes: '', critical: true },
    { id: '1.4', category: 'Foundation & Support', number: '1.4', text: 'Footings are adequate for soil conditions and load requirements', status: '', notes: '', critical: true },
    { id: '1.5', category: 'Foundation & Support', number: '1.5', text: 'Drainage provided to prevent water accumulation under scaffold', status: '', notes: '', critical: false },

    // Platform & Planking
    { id: '2.1', category: 'Platform & Planking', number: '2.1', text: 'Platforms fully planked or decked between front uprights and guardrail supports', status: '', notes: '', critical: true },
    { id: '2.2', category: 'Platform & Planking', number: '2.2', text: 'Platform width is minimum 18 inches (46 cm) for work platforms', status: '', notes: '', critical: true },
    { id: '2.3', category: 'Platform & Planking', number: '2.3', text: 'Platforms/planks overlap supports by minimum 6 inches and maximum 12 inches', status: '', notes: '', critical: true },
    { id: '2.4', category: 'Platform & Planking', number: '2.4', text: 'Platform planks are scaffold grade or equivalent (minimum 1500 psi fiber stress)', status: '', notes: '', critical: true },
    { id: '2.5', category: 'Platform & Planking', number: '2.5', text: 'Platforms secured to prevent movement or uplift', status: '', notes: '', critical: true },
    { id: '2.6', category: 'Platform & Planking', number: '2.6', text: 'Maximum gap between planks is 1 inch, except at uprights where gap cannot exceed 9.5 inches', status: '', notes: '', critical: false },

    // Guardrails & Fall Protection
    { id: '3.1', category: 'Guardrails & Fall Protection', number: '3.1', text: 'Guardrails installed on all open sides and ends of platforms more than 10 feet above ground', status: '', notes: '', critical: true },
    { id: '3.2', category: 'Guardrails & Fall Protection', number: '3.2', text: 'Top rail height between 38-45 inches (97-114 cm) above platform surface', status: '', notes: '', critical: true },
    { id: '3.3', category: 'Guardrails & Fall Protection', number: '3.3', text: 'Midrails installed approximately midway between toprail and platform surface', status: '', notes: '', critical: true },
    { id: '3.4', category: 'Guardrails & Fall Protection', number: '3.4', text: 'Toeboards minimum 4 inches (10 cm) high installed where materials could fall', status: '', notes: '', critical: false },
    { id: '3.5', category: 'Guardrails & Fall Protection', number: '3.5', text: 'Guardrail system capable of withstanding 200 lbs force in any direction', status: '', notes: '', critical: true },
    { id: '3.6', category: 'Guardrails & Fall Protection', number: '3.6', text: 'Personal fall arrest systems provided where guardrails are not feasible', status: '', notes: '', critical: true },

    // Access & Egress
    { id: '4.1', category: 'Access & Egress', number: '4.1', text: 'Safe access provided via ladder, stair tower, ramp, or walkway', status: '', notes: '', critical: true },
    { id: '4.2', category: 'Access & Egress', number: '4.2', text: 'Ladder extends minimum 3 feet (1 m) above landing platform', status: '', notes: '', critical: true },
    { id: '4.3', category: 'Access & Egress', number: '4.3', text: 'Cross-braces not used as access unless specifically designed for that purpose', status: '', notes: '', critical: true },
    { id: '4.4', category: 'Access & Egress', number: '4.4', text: 'Access points located to minimize fall hazards', status: '', notes: '', critical: false },
    { id: '4.5', category: 'Access & Egress', number: '4.5', text: 'Stair towers have proper railings and meet OSHA stair requirements', status: '', notes: '', critical: false },

    // Stability & Bracing
    { id: '5.1', category: 'Stability & Bracing', number: '5.1', text: 'Scaffold tied to structure at proper intervals (4:1 height to base ratio maximum)', status: '', notes: '', critical: true },
    { id: '5.2', category: 'Stability & Bracing', number: '5.2', text: 'All braces, ties, and guys properly installed and secured', status: '', notes: '', critical: true },
    { id: '5.3', category: 'Stability & Bracing', number: '5.3', text: 'Ties installed per manufacturer recommendations (typically every 26-30 feet)', status: '', notes: '', critical: true },
    { id: '5.4', category: 'Stability & Bracing', number: '5.4', text: 'Diagonal bracing installed in both directions for frame scaffolds', status: '', notes: '', critical: true },
    { id: '5.5', category: 'Stability & Bracing', number: '5.5', text: 'Outrigger beams properly secured and do not extend beyond their supports', status: '', notes: '', critical: false },

    // Load Capacity & Use
    { id: '6.1', category: 'Load Capacity & Use', number: '6.1', text: 'Scaffold load capacity clearly posted and not exceeded', status: '', notes: '', critical: true },
    { id: '6.2', category: 'Load Capacity & Use', number: '6.2', text: 'Materials and equipment properly distributed on platform', status: '', notes: '', critical: true },
    { id: '6.3', category: 'Load Capacity & Use', number: '6.3', text: 'No makeshift devices used to increase height (boxes, ladders, etc.)', status: '', notes: '', critical: true },
    { id: '6.4', category: 'Load Capacity & Use', number: '6.4', text: 'Scaffold not loaded beyond its maximum intended load', status: '', notes: '', critical: true },

    // Training & Competency
    { id: '7.1', category: 'Training & Competency', number: '7.1', text: 'All workers trained on scaffold hazards and proper use procedures', status: '', notes: '', critical: true },
    { id: '7.2', category: 'Training & Competency', number: '7.2', text: 'Competent person has inspected scaffold before each work shift', status: '', notes: '', critical: true },
    { id: '7.3', category: 'Training & Competency', number: '7.3', text: 'Scaffold erected, moved, or dismantled under supervision of competent person', status: '', notes: '', critical: true },
    { id: '7.4', category: 'Training & Competency', number: '7.4', text: 'Training records maintained and available for review', status: '', notes: '', critical: false },

    // Environmental & Special Conditions
    { id: '8.1', category: 'Environmental & Special Conditions', number: '8.1', text: 'Electrical hazards identified and appropriate clearances maintained', status: '', notes: '', critical: true },
    { id: '8.2', category: 'Environmental & Special Conditions', number: '8.2', text: 'Weather conditions suitable for scaffold use (wind speed < 25 mph)', status: '', notes: '', critical: true },
    { id: '8.3', category: 'Environmental & Special Conditions', number: '8.3', text: 'Fall protection provided for work near water or other hazards', status: '', notes: '', critical: true },
    { id: '8.4', category: 'Environmental & Special Conditions', number: '8.4', text: 'Scaffold protected from vehicular traffic where applicable', status: '', notes: '', critical: false }
  ])

  const [collapsedSections, setCollapsedSections] = useState<Set<string>>(new Set())
  const [showCriticalOnly, setShowCriticalOnly] = useState(false)

  // Fix TypeScript error by using Array.from instead of spread operator
  const categories = Array.from(new Set(checklistItems.map(item => item.category)))

  const updateItemStatus = useCallback((itemId: string, status: 'pass' | 'fail' | 'na' | '') => {
    setChecklistItems(prev => 
      prev.map(item => 
        item.id === itemId ? { ...item, status } : item
      )
    )
  }, [])

  const updateItemNotes = useCallback((itemId: string, notes: string) => {
    setChecklistItems(prev => 
      prev.map(item => 
        item.id === itemId ? { ...item, notes } : item
      )
    )
  }, [])

  const toggleSection = useCallback((category: string) => {
    setCollapsedSections(prev => {
      const newSet = new Set(prev)
      if (newSet.has(category)) {
        newSet.delete(category)
      } else {
        newSet.add(category)
      }
      return newSet
    })
  }, [])

  const getStats = useCallback(() => {
    const total = checklistItems.length
    const passed = checklistItems.filter(item => item.status === 'pass').length
    const failed = checklistItems.filter(item => item.status === 'fail').length
    const na = checklistItems.filter(item => item.status === 'na').length
    const pending = total - passed - failed - na
    const criticalFailed = checklistItems.filter(item => item.critical && item.status === 'fail').length
    
    return { total, passed, failed, na, pending, criticalFailed }
  }, [checklistItems])

  const generateReport = useCallback(() => {
    const stats = getStats()
    const failedItems = checklistItems.filter(item => item.status === 'fail')
    const criticalFailures = failedItems.filter(item => item.critical)
    
    const reportData = {
      projectInfo,
      stats,
      failedItems,
      criticalFailures,
      timestamp: new Date().toISOString()
    }

    // Create downloadable report
    const reportContent = `
OSHA SCAFFOLDING SAFETY INSPECTION REPORT
==========================================

Project Information:
- Project Name: ${projectInfo.projectName}
- Location: ${projectInfo.location}
- Inspector: ${projectInfo.inspector}
- Date: ${projectInfo.date}
- Scaffold Type: ${projectInfo.scaffoldType}
- Height: ${projectInfo.height}
- Contractor: ${projectInfo.contractor}
- Permit Number: ${projectInfo.permitNumber}

Inspection Summary:
- Total Items: ${stats.total}
- Passed: ${stats.passed}
- Failed: ${stats.failed}
- N/A: ${stats.na}
- Pending: ${stats.pending}
- Critical Failures: ${stats.criticalFailed}

${stats.criticalFailed > 0 ? 'CRITICAL SAFETY VIOLATIONS FOUND - SCAFFOLD NOT SAFE FOR USE' : 'All critical items passed inspection'}

${failedItems.length > 0 ? `
Failed Items:
${failedItems.map(item => `- ${item.number}: ${item.text}${item.notes ? ` (Notes: ${item.notes})` : ''}`).join('\n')}
` : 'No failed items'}

Report generated: ${new Date().toLocaleString()}
    `.trim()

    const blob = new Blob([reportContent], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `OSHA_Scaffold_Inspection_${projectInfo.projectName || 'Report'}_${projectInfo.date}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }, [projectInfo, checklistItems, getStats])

  const clearForm = useCallback(() => {
    if (confirm('Are you sure you want to clear all data? This action cannot be undone.')) {
      setProjectInfo({
        projectName: '',
        location: '',
        inspector: '',
        date: new Date().toISOString().split('T')[0],
        scaffoldType: '',
        height: '',
        contractor: '',
        permitNumber: ''
      })
      setChecklistItems(prev => prev.map(item => ({ ...item, status: '', notes: '' })))
    }
  }, [])

  const stats = getStats()
  const filteredItems = showCriticalOnly ? checklistItems.filter(item => item.critical) : checklistItems

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-red-600 to-red-700 text-white shadow-2xl">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold mb-2">OSHA Scaffolding Safety Checklist</h1>
            <p className="text-red-100 text-lg">Comprehensive inspection based on 29 CFR 1926.451-454</p>
            <div className="mt-4 inline-flex items-center bg-red-800/30 px-4 py-2 rounded-full">
              <AlertTriangle className="w-5 h-5 mr-2" />
              <span className="text-sm font-medium">Safety Critical - Complete All Sections</span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Project Information */}
        <div className="bg-white rounded-2xl shadow-xl mb-8 overflow-hidden">
          <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-4">
            <h2 className="text-2xl font-bold flex items-center">
              <FileText className="w-6 h-6 mr-2" />
              Project Information
            </h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {Object.entries({
                projectName: 'Project Name',
                location: 'Location',
                inspector: 'Inspector Name',
                date: 'Inspection Date',
                scaffoldType: 'Scaffold Type',
                height: 'Scaffold Height (ft)',
                contractor: 'Contractor',
                permitNumber: 'Permit Number'
              }).map(([key, label]) => (
                <div key={key} className="space-y-2">
                  <label className="block text-sm font-semibold text-gray-700">{label}</label>
                  <input
                    type={key === 'date' ? 'date' : 'text'}
                    value={projectInfo[key as keyof ProjectInfo]}
                    onChange={(e) => setProjectInfo(prev => ({ ...prev, [key]: e.target.value }))}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                    placeholder={key === 'date' ? '' : `Enter ${label.toLowerCase()}`}
                  />
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Stats Dashboard */}
        <div className="bg-white rounded-2xl shadow-xl mb-8 overflow-hidden">
          <div className="bg-gradient-to-r from-green-600 to-green-700 text-white px-6 py-4">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">Inspection Progress</h2>
              <button
                onClick={() => setShowCriticalOnly(!showCriticalOnly)}
                className="flex items-center bg-green-800/30 hover:bg-green-800/50 px-4 py-2 rounded-lg transition-colors"
              >
                {showCriticalOnly ? <Eye className="w-4 h-4 mr-2" /> : <EyeOff className="w-4 h-4 mr-2" />}
                {showCriticalOnly ? 'Show All' : 'Critical Only'}
              </button>
            </div>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
              {[
                { label: 'Total', value: stats.total, color: 'bg-gray-100 text-gray-800' },
                { label: 'Passed', value: stats.passed, color: 'bg-green-100 text-green-800' },
                { label: 'Failed', value: stats.failed, color: 'bg-red-100 text-red-800' },
                { label: 'N/A', value: stats.na, color: 'bg-gray-100 text-gray-600' },
                { label: 'Pending', value: stats.pending, color: 'bg-yellow-100 text-yellow-800' },
                { label: 'Critical Fails', value: stats.criticalFailed, color: 'bg-red-200 text-red-900 font-bold' }
              ].map((stat) => (
                <div key={stat.label} className={`${stat.color} rounded-xl p-4 text-center`}>
                  <div className="text-2xl font-bold">{stat.value}</div>
                  <div className="text-sm">{stat.label}</div>
                </div>
              ))}
            </div>
            {stats.criticalFailed > 0 && (
              <div className="mt-4 bg-red-50 border-l-4 border-red-500 p-4 rounded">
                <div className="flex items-center">
                  <AlertTriangle className="w-5 h-5 text-red-500 mr-2" />
                  <span className="text-red-800 font-semibold">
                    Critical safety violations detected. Scaffold is NOT SAFE for use.
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Checklist Sections */}
        {categories.map((category) => {
          const categoryItems = filteredItems.filter(item => item.category === category)
          const isCollapsed = collapsedSections.has(category)
          
          return (
            <div key={category} className="bg-white rounded-2xl shadow-xl mb-6 overflow-hidden">
              <button
                onClick={() => toggleSection(category)}
                className="w-full bg-gradient-to-r from-slate-600 to-slate-700 text-white px-6 py-4 text-left hover:from-slate-700 hover:to-slate-800 transition-all duration-200"
              >
                <div className="flex justify-between items-center">
                  <h3 className="text-xl font-bold">{category}</h3>
                  <div className="flex items-center space-x-4">
                    <span className="text-sm bg-slate-800/30 px-3 py-1 rounded-full">
                      {categoryItems.length} items
                    </span>
                    <div className={`transform transition-transform ${isCollapsed ? '-rotate-90' : 'rotate-0'}`}>
                      ▼
                    </div>
                  </div>
                </div>
              </button>
              
              {!isCollapsed && (
                <div className="p-6 space-y-4">
                  {categoryItems.map((item) => (
                    <div
                      key={item.id}
                      className={`border-l-4 ${
                        item.status === 'pass' ? 'border-green-500 bg-green-50' :
                        item.status === 'fail' ? 'border-red-500 bg-red-50' :
                        item.status === 'na' ? 'border-gray-400 bg-gray-50' :
                        'border-gray-200 bg-white'
                      } rounded-r-lg p-4 transition-all duration-200 hover:shadow-md`}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <div className="flex items-center mb-2">
                            <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-semibold mr-3">
                              {item.number}
                            </span>
                            {item.critical && (
                              <span className="bg-red-100 text-red-800 px-2 py-1 rounded text-xs font-bold mr-2">
                                CRITICAL
                              </span>
                            )}
                          </div>
                          <p className="text-gray-800 leading-relaxed">{item.text}</p>
                        </div>
                      </div>
                      
                      <div className="flex flex-wrap gap-3 mb-3">
                        {[
                          { value: 'pass', label: 'Pass', icon: CheckCircle, color: 'bg-green-500 hover:bg-green-600' },
                          { value: 'fail', label: 'Fail', icon: XCircle, color: 'bg-red-500 hover:bg-red-600' },
                          { value: 'na', label: 'N/A', icon: AlertTriangle, color: 'bg-gray-500 hover:bg-gray-600' }
                        ].map(({ value, label, icon: Icon, color }) => (
                          <button
                            key={value}
                            onClick={() => updateItemStatus(item.id, value as any)}
                            className={`flex items-center px-4 py-2 rounded-lg text-white font-medium transition-all duration-200 ${
                              item.status === value ? color : 'bg-gray-300 hover:bg-gray-400'
                            }`}
                          >
                            <Icon className="w-4 h-4 mr-2" />
                            {label}
                          </button>
                        ))}
                      </div>
                      
                      <textarea
                        value={item.notes}
                        onChange={(e) => updateItemNotes(item.id, e.target.value)}
                        placeholder="Add notes, observations, or corrective actions..."
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                        rows={2}
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>
          )
        })}

        {/* Action Buttons */}
        <div className="bg-white rounded-2xl shadow-xl p-6">
          <div className="flex flex-wrap gap-4 justify-center">
            <button
              onClick={generateReport}
              className="flex items-center bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
            >
              <Download className="w-5 h-5 mr-2" />
              Generate Report
            </button>
            <button
              onClick={clearForm}
              className="flex items-center bg-gray-600 hover:bg-gray-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
            >
              <RotateCcw className="w-5 h-5 mr-2" />
              Clear Form
            </button>
            <button
              onClick={() => window.print()}
              className="flex items-center bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
            >
              <FileText className="w-5 h-5 mr-2" />
              Print Checklist
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default OSHAScaffoldingChecklist