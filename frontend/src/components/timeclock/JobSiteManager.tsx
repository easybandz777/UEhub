'use client'

import { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { MapPin, Plus, QrCode, Edit, Trash2, Download, AlertCircle, CheckCircle } from 'lucide-react'

interface JobSite {
  id: string
  name: string
  description?: string
  address?: string
  latitude?: number
  longitude?: number
  radius_meters: number
  qr_code_data: string
  is_active: boolean
  created_at: string
}

interface JobSiteWithQR extends JobSite {
  qr_code_image: string
}

export function JobSiteManager() {
  const [jobSites, setJobSites] = useState<JobSite[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [selectedJobSite, setSelectedJobSite] = useState<JobSiteWithQR | null>(null)
  const [isQRDialogOpen, setIsQRDialogOpen] = useState(false)

  useEffect(() => {
    loadJobSites()
  }, [])

  const loadJobSites = async () => {
    try {
      setLoading(true)
      const response = await apiClient.get('/timeclock/job-sites')
      setJobSites(response.data)
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to load job sites')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateJobSite = async (formData: FormData) => {
    try {
      const jobSiteData = {
        name: formData.get('name') as string,
        description: formData.get('description') as string,
        address: formData.get('address') as string,
        latitude: formData.get('latitude') ? parseFloat(formData.get('latitude') as string) : undefined,
        longitude: formData.get('longitude') ? parseFloat(formData.get('longitude') as string) : undefined,
        radius_meters: parseInt(formData.get('radius_meters') as string) || 100,
      }

      await apiClient.post('/timeclock/job-sites', jobSiteData)
      setIsCreateDialogOpen(false)
      loadJobSites()
      setError(null)
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to create job site')
    }
  }

  const handleShowQR = async (jobSite: JobSite) => {
    try {
      setLoading(true)
      const response = await apiClient.get(`/timeclock/job-sites/${jobSite.id}/qr`)
      setSelectedJobSite(response.data)
      setIsQRDialogOpen(true)
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to load QR code')
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadQR = () => {
    if (!selectedJobSite) return

    const link = document.createElement('a')
    link.href = selectedJobSite.qr_code_image
    link.download = `${selectedJobSite.name.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_qr_code.png`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const handleToggleActive = async (jobSite: JobSite) => {
    try {
      await apiClient.put(`/timeclock/job-sites/${jobSite.id}`, {
        is_active: !jobSite.is_active
      })
      loadJobSites()
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to update job site')
    }
  }

  if (loading && jobSites.length === 0) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2">Loading job sites...</span>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Job Site Management</h2>
          <p className="text-gray-600">Create and manage job sites with QR codes</p>
        </div>
        
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button className="flex items-center gap-2">
              <Plus className="w-4 h-4" />
              Create Job Site
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Job Site</DialogTitle>
              <DialogDescription>
                Create a new job site with QR code for employee clock in/out
              </DialogDescription>
            </DialogHeader>
            <form action={handleCreateJobSite} className="space-y-4">
              <div>
                <Label htmlFor="name">Job Site Name *</Label>
                <Input id="name" name="name" required placeholder="e.g. Downtown Office Building" />
              </div>
              
              <div>
                <Label htmlFor="description">Description</Label>
                <Textarea id="description" name="description" placeholder="Brief description of the job site" />
              </div>
              
              <div>
                <Label htmlFor="address">Address</Label>
                <Textarea id="address" name="address" placeholder="Full address of the job site" />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="latitude">Latitude</Label>
                  <Input 
                    id="latitude" 
                    name="latitude" 
                    type="number" 
                    step="any" 
                    placeholder="40.7128" 
                  />
                </div>
                <div>
                  <Label htmlFor="longitude">Longitude</Label>
                  <Input 
                    id="longitude" 
                    name="longitude" 
                    type="number" 
                    step="any" 
                    placeholder="-74.0060" 
                  />
                </div>
              </div>
              
              <div>
                <Label htmlFor="radius_meters">Geofence Radius (meters)</Label>
                <Input 
                  id="radius_meters" 
                  name="radius_meters" 
                  type="number" 
                  defaultValue={100}
                  min={10}
                  max={1000}
                />
              </div>
              
              <div className="flex justify-end gap-2">
                <Button type="button" variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit">Create Job Site</Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {jobSites.map((jobSite) => (
          <Card key={jobSite.id} className={!jobSite.is_active ? 'opacity-60' : ''}>
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <MapPin className="w-4 h-4" />
                    {jobSite.name}
                  </CardTitle>
                  {jobSite.description && (
                    <CardDescription className="mt-1">
                      {jobSite.description}
                    </CardDescription>
                  )}
                </div>
                <Badge variant={jobSite.is_active ? 'default' : 'secondary'}>
                  {jobSite.is_active ? 'Active' : 'Inactive'}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {jobSite.address && (
                  <p className="text-sm text-gray-600">{jobSite.address}</p>
                )}
                
                {jobSite.latitude && jobSite.longitude && (
                  <p className="text-xs text-gray-500">
                    📍 {jobSite.latitude.toFixed(6)}, {jobSite.longitude.toFixed(6)}
                    <br />
                    Radius: {jobSite.radius_meters}m
                  </p>
                )}
                
                <div className="flex gap-2 flex-wrap">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleShowQR(jobSite)}
                    className="flex items-center gap-1"
                  >
                    <QrCode className="w-3 h-3" />
                    QR Code
                  </Button>
                  
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleToggleActive(jobSite)}
                    className="flex items-center gap-1"
                  >
                    {jobSite.is_active ? 'Deactivate' : 'Activate'}
                  </Button>
                </div>
                
                <p className="text-xs text-gray-400">
                  Created: {new Date(jobSite.created_at).toLocaleDateString()}
                </p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {jobSites.length === 0 && !loading && (
        <Card>
          <CardContent className="text-center py-8">
            <MapPin className="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Job Sites Yet</h3>
            <p className="text-gray-600 mb-4">
              Create your first job site to start tracking employee hours
            </p>
            <Button onClick={() => setIsCreateDialogOpen(true)}>
              Create Job Site
            </Button>
          </CardContent>
        </Card>
      )}

      {/* QR Code Dialog */}
      <Dialog open={isQRDialogOpen} onOpenChange={setIsQRDialogOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <QrCode className="w-5 h-5" />
              QR Code - {selectedJobSite?.name}
            </DialogTitle>
            <DialogDescription>
              Print or display this QR code at the job site for employees to scan
            </DialogDescription>
          </DialogHeader>
          
          {selectedJobSite && (
            <div className="space-y-4">
              <div className="flex justify-center">
                <img 
                  src={selectedJobSite.qr_code_image} 
                  alt={`QR Code for ${selectedJobSite.name}`}
                  className="w-64 h-64 border rounded-lg"
                />
              </div>
              
              <div className="text-center space-y-2">
                <p className="font-semibold">{selectedJobSite.name}</p>
                {selectedJobSite.address && (
                  <p className="text-sm text-gray-600">{selectedJobSite.address}</p>
                )}
                <p className="text-xs text-gray-500">
                  QR Code ID: {selectedJobSite.qr_code_data}
                </p>
              </div>
              
              <div className="flex gap-2">
                <Button onClick={handleDownloadQR} className="flex-1">
                  <Download className="w-4 h-4 mr-2" />
                  Download
                </Button>
                <Button variant="outline" onClick={() => setIsQRDialogOpen(false)}>
                  Close
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
