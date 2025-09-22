'use client'

import { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Clock, MapPin, Calendar, CheckCircle, XCircle, AlertCircle } from 'lucide-react'

interface TimeEntry {
  id: string
  job_site_id: string
  clock_in_time: string
  clock_out_time?: string
  break_start_time?: string
  break_end_time?: string
  total_hours?: number
  break_hours?: number
  notes?: string
  is_approved: boolean
  approved_at?: string
  job_site: {
    name: string
    address?: string
  }
  user_name: string
  approved_by_name?: string
}

interface TimeEntryListProps {
  userId?: string
}

export function TimeEntryList({ userId }: TimeEntryListProps) {
  const [timeEntries, setTimeEntries] = useState<TimeEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadTimeEntries()
  }, [userId])

  const loadTimeEntries = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (userId) {
        params.append('user_id', userId)
      }
      params.append('limit', '50')
      
      const response = await apiClient.get<TimeEntry[]>(`/timeclock/time-entries?${params}`)
      setTimeEntries(response.data)
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to load time entries')
    } finally {
      setLoading(false)
    }
  }

  const formatDuration = (hours?: number) => {
    if (!hours) return 'N/A'
    const h = Math.floor(hours)
    const m = Math.round((hours - h) * 60)
    return `${h}h ${m}m`
  }

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  const getStatusBadge = (entry: TimeEntry) => {
    if (!entry.clock_out_time) {
      return <Badge className="bg-green-100 text-green-800">Active</Badge>
    }
    if (entry.is_approved) {
      return <Badge className="bg-blue-100 text-blue-800">Approved</Badge>
    }
    return <Badge variant="secondary">Pending Approval</Badge>
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2">Loading time entries...</span>
      </div>
    )
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Time Entries</h2>
        <p className="text-gray-600">Your recent work hours and time tracking</p>
      </div>

      {timeEntries.length === 0 ? (
        <Card>
          <CardContent className="text-center py-8">
            <Clock className="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Time Entries Yet</h3>
            <p className="text-gray-600">
              Start by scanning a QR code to clock in at a job site
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {timeEntries.map((entry) => (
            <Card key={entry.id}>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      <MapPin className="w-4 h-4" />
                      {entry.job_site.name}
                    </CardTitle>
                    {entry.job_site.address && (
                      <CardDescription>{entry.job_site.address}</CardDescription>
                    )}
                  </div>
                  {getStatusBadge(entry)}
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm">
                      <Clock className="w-4 h-4 text-green-600" />
                      <span className="font-medium">Clock In:</span>
                      <span>{formatDateTime(entry.clock_in_time)}</span>
                    </div>
                    
                    {entry.clock_out_time && (
                      <div className="flex items-center gap-2 text-sm">
                        <Clock className="w-4 h-4 text-red-600" />
                        <span className="font-medium">Clock Out:</span>
                        <span>{formatDateTime(entry.clock_out_time)}</span>
                      </div>
                    )}
                    
                    {entry.break_start_time && (
                      <div className="flex items-center gap-2 text-sm">
                        <Clock className="w-4 h-4 text-orange-600" />
                        <span className="font-medium">Break:</span>
                        <span>
                          {formatDateTime(entry.break_start_time)}
                          {entry.break_end_time && ` - ${formatDateTime(entry.break_end_time)}`}
                        </span>
                      </div>
                    )}
                  </div>
                  
                  <div className="space-y-2">
                    {entry.total_hours && (
                      <div className="flex items-center gap-2 text-sm">
                        <Calendar className="w-4 h-4 text-blue-600" />
                        <span className="font-medium">Total Hours:</span>
                        <span className="font-semibold">{formatDuration(entry.total_hours)}</span>
                      </div>
                    )}
                    
                    {entry.break_hours && (
                      <div className="flex items-center gap-2 text-sm">
                        <Calendar className="w-4 h-4 text-orange-600" />
                        <span className="font-medium">Break Time:</span>
                        <span>{formatDuration(entry.break_hours)}</span>
                      </div>
                    )}
                    
                    {entry.is_approved && entry.approved_by_name && (
                      <div className="flex items-center gap-2 text-sm">
                        <CheckCircle className="w-4 h-4 text-green-600" />
                        <span className="font-medium">Approved by:</span>
                        <span>{entry.approved_by_name}</span>
                      </div>
                    )}
                  </div>
                </div>
                
                {entry.notes && (
                  <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm">
                      <span className="font-medium">Notes:</span> {entry.notes}
                    </p>
                  </div>
                )}
                
                {!entry.clock_out_time && (
                  <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                      <span className="text-sm font-medium text-green-800">
                        Currently active - you are clocked in
                      </span>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
