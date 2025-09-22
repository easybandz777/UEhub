'use client'

import { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Clock, Users, MapPin, CheckCircle, AlertCircle, TrendingUp } from 'lucide-react'

interface TimeclockStats {
  total_employees_clocked_in: number
  total_active_job_sites: number
  total_hours_today: number
  total_hours_this_week: number
  pending_approvals: number
}

export function TimeclockDashboard() {
  const [stats, setStats] = useState<TimeclockStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadStats()
    
    // Refresh stats every 30 seconds
    const interval = setInterval(loadStats, 30000)
    return () => clearInterval(interval)
  }, [])

  const loadStats = async () => {
    try {
      const response = await apiClient.get('/timeclock/stats')
      setStats(response.data)
      setError(null)
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to load statistics')
    } finally {
      setLoading(false)
    }
  }

  const formatHours = (hours: number) => {
    const h = Math.floor(hours)
    const m = Math.round((hours - h) * 60)
    return `${h}h ${m}m`
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2">Loading dashboard...</span>
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

  if (!stats) {
    return null
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Timeclock Dashboard</h2>
        <p className="text-gray-600">Overview of employee time tracking and job sites</p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Employees Clocked In</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_employees_clocked_in}</div>
            <p className="text-xs text-muted-foreground">
              Currently active
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Job Sites</CardTitle>
            <MapPin className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_active_job_sites}</div>
            <p className="text-xs text-muted-foreground">
              Available for clock in
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Approvals</CardTitle>
            <AlertCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.pending_approvals}</div>
            <p className="text-xs text-muted-foreground">
              Time entries awaiting approval
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Hours Today</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatHours(stats.total_hours_today)}</div>
            <p className="text-xs text-muted-foreground">
              Total worked today
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Hours This Week</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatHours(stats.total_hours_this_week)}</div>
            <p className="text-xs text-muted-foreground">
              Total worked this week
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">System Status</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">Online</div>
            <p className="text-xs text-muted-foreground">
              All systems operational
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Status Cards */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="w-5 h-5" />
              Employee Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm">Currently Working</span>
                <Badge className="bg-green-100 text-green-800">
                  {stats.total_employees_clocked_in} employees
                </Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Available Job Sites</span>
                <Badge variant="outline">
                  {stats.total_active_job_sites} sites
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5" />
              Pending Actions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm">Time Entry Approvals</span>
                <Badge variant={stats.pending_approvals > 0 ? "destructive" : "outline"}>
                  {stats.pending_approvals} pending
                </Badge>
              </div>
              {stats.pending_approvals > 0 && (
                <p className="text-xs text-amber-600">
                  ⚠️ Time entries require admin approval
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>
            Common administrative tasks
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            <Badge variant="outline" className="cursor-pointer hover:bg-gray-100">
              View All Time Entries
            </Badge>
            <Badge variant="outline" className="cursor-pointer hover:bg-gray-100">
              Export Timesheet
            </Badge>
            <Badge variant="outline" className="cursor-pointer hover:bg-gray-100">
              Manage Job Sites
            </Badge>
            <Badge variant="outline" className="cursor-pointer hover:bg-gray-100">
              User Management
            </Badge>
          </div>
        </CardContent>
      </Card>

      <div className="text-xs text-gray-500 text-center">
        Last updated: {new Date().toLocaleTimeString()} • Auto-refresh every 30 seconds
      </div>
    </div>
  )
}
