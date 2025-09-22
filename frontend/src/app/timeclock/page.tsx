'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/components/auth/AuthProvider'
import { apiClient } from '@/lib/api'
import { QRScanner } from '@/components/timeclock/QRScanner'
import { TimeclockDashboard } from '@/components/timeclock/TimeclockDashboard'
import { JobSiteManager } from '@/components/timeclock/JobSiteManager'
import { TimeEntryList } from '@/components/timeclock/TimeEntryList'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Clock, QrCode, MapPin, Users, BarChart3 } from 'lucide-react'

interface ActiveTimeEntry {
  id: string
  job_site_id: string
  clock_in_time: string
  job_site?: {
    name: string
    address?: string
  }
}

export default function TimeclockPage() {
  const { user, isAuthenticated } = useAuth()
  const [activeTimeEntry, setActiveTimeEntry] = useState<ActiveTimeEntry | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (isAuthenticated) {
      loadActiveTimeEntry()
    }
  }, [isAuthenticated])

  const loadActiveTimeEntry = async () => {
    try {
      const response = await apiClient.get<ActiveTimeEntry | null>('/timeclock/time-entries/active')
      setActiveTimeEntry(response.data)
    } catch (error) {
      console.error('Failed to load active time entry:', error)
      setActiveTimeEntry(null)
    } finally {
      setLoading(false)
    }
  }

  const handleClockAction = () => {
    // Refresh active time entry after clock in/out
    loadActiveTimeEntry()
  }

  if (!isAuthenticated) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="w-6 h-6" />
              Timeclock System
            </CardTitle>
            <CardDescription>
              Please log in to access the timeclock system.
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2">Loading timeclock...</span>
        </div>
      </div>
    )
  }

  const isAdmin = user?.role === 'admin' || user?.role === 'superadmin'

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Clock className="w-8 h-8" />
          Timeclock System
        </h1>
        <p className="text-gray-600 mt-2">
          Track your work hours with QR code scanning
        </p>
      </div>

      {/* Current Status Card */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="w-5 h-5" />
            Current Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          {activeTimeEntry ? (
            <div className="flex items-center gap-4 p-4 bg-green-50 rounded-lg border border-green-200">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
              <div>
                <p className="font-semibold text-green-800">
                  Currently clocked in
                </p>
                <p className="text-sm text-green-600">
                  {activeTimeEntry.job_site?.name || 'Unknown Job Site'}
                </p>
                <p className="text-xs text-green-500">
                  Since: {new Date(activeTimeEntry.clock_in_time).toLocaleString()}
                </p>
              </div>
            </div>
          ) : (
            <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
              <div className="w-3 h-3 bg-gray-400 rounded-full"></div>
              <div>
                <p className="font-semibold text-gray-800">
                  Not clocked in
                </p>
                <p className="text-sm text-gray-600">
                  Scan a QR code to clock in at a job site
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <Tabs defaultValue="scanner" className="w-full">
        <TabsList className="grid w-full grid-cols-2 lg:grid-cols-4">
          <TabsTrigger value="scanner" className="flex items-center gap-2">
            <QrCode className="w-4 h-4" />
            QR Scanner
          </TabsTrigger>
          <TabsTrigger value="entries" className="flex items-center gap-2">
            <Clock className="w-4 h-4" />
            My Hours
          </TabsTrigger>
          {isAdmin && (
            <>
              <TabsTrigger value="jobsites" className="flex items-center gap-2">
                <MapPin className="w-4 h-4" />
                Job Sites
              </TabsTrigger>
              <TabsTrigger value="dashboard" className="flex items-center gap-2">
                <BarChart3 className="w-4 h-4" />
                Dashboard
              </TabsTrigger>
            </>
          )}
        </TabsList>

        <TabsContent value="scanner" className="mt-6">
          <QRScanner 
            activeTimeEntry={activeTimeEntry}
            onClockAction={handleClockAction}
          />
        </TabsContent>

        <TabsContent value="entries" className="mt-6">
          <TimeEntryList userId={user?.id} />
        </TabsContent>

        {isAdmin && (
          <>
            <TabsContent value="jobsites" className="mt-6">
              <JobSiteManager />
            </TabsContent>

            <TabsContent value="dashboard" className="mt-6">
              <TimeclockDashboard />
            </TabsContent>
          </>
        )}
      </Tabs>
    </div>
  )
}
