'use client'

import { useState, useEffect, useRef } from 'react'
import { Html5QrcodeScanner, Html5QrcodeScannerConfig } from 'html5-qrcode'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { QrCode, Camera, MapPin, Clock, Coffee, LogOut, AlertCircle, CheckCircle } from 'lucide-react'

interface QRScannerProps {
  activeTimeEntry: any
  onClockAction: () => void
}

interface ScanResult {
  job_site: {
    id: string
    name: string
    address?: string
    description?: string
  }
  can_clock_in: boolean
  can_clock_out: boolean
  active_time_entry_id?: string
  message: string
}

export function QRScanner({ activeTimeEntry, onClockAction }: QRScannerProps) {
  const [scanResult, setScanResult] = useState<ScanResult | null>(null)
  const [isScanning, setIsScanning] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [location, setLocation] = useState<{ lat: number; lng: number } | null>(null)
  const scannerRef = useRef<Html5QrcodeScanner | null>(null)
  const elementId = 'qr-scanner'

  useEffect(() => {
    // Get user location for geofencing
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude
          })
        },
        (error) => {
          console.warn('Location access denied:', error)
        }
      )
    }

    return () => {
      stopScanner()
    }
  }, [])

  const startScanner = () => {
    if (scannerRef.current) {
      stopScanner()
    }

    const config: Html5QrcodeScannerConfig = {
      fps: 10,
      qrbox: { width: 250, height: 250 },
      aspectRatio: 1.0,
      disableFlip: false,
      supportedScanTypes: [0], // QR Code only
    }

    scannerRef.current = new Html5QrcodeScanner(elementId, config, false)
    
    scannerRef.current.render(
      (decodedText) => {
        handleScanSuccess(decodedText)
      },
      (error) => {
        // Ignore scan errors, they're too frequent
        console.debug('QR scan error:', error)
      }
    )

    setIsScanning(true)
    setError(null)
    setScanResult(null)
  }

  const stopScanner = () => {
    if (scannerRef.current) {
      scannerRef.current.clear()
      scannerRef.current = null
    }
    setIsScanning(false)
  }

  const handleScanSuccess = async (qrCodeData: string) => {
    stopScanner()
    setLoading(true)
    setError(null)

    try {
      const response = await apiClient.post('/timeclock/scan', {
        qr_code_data: qrCodeData
      })
      
      setScanResult(response.data)
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to process QR code')
    } finally {
      setLoading(false)
    }
  }

  const handleClockIn = async () => {
    if (!scanResult) return

    setLoading(true)
    setError(null)

    try {
      const requestData: any = {
        qr_code_data: scanResult.job_site.id, // This should be the actual QR code data
        notes: ''
      }

      if (location) {
        requestData.location_lat = location.lat
        requestData.location_lng = location.lng
      }

      const response = await apiClient.post('/timeclock/clock-in', requestData)
      
      // Show success message
      setError(null)
      setScanResult(null)
      onClockAction()
      
      // Show success alert
      alert(`✅ ${response.data.message}`)
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to clock in')
    } finally {
      setLoading(false)
    }
  }

  const handleClockOut = async () => {
    if (!scanResult || !scanResult.active_time_entry_id) return

    setLoading(true)
    setError(null)

    try {
      const requestData: any = {
        time_entry_id: scanResult.active_time_entry_id,
        notes: ''
      }

      if (location) {
        requestData.location_lat = location.lat
        requestData.location_lng = location.lng
      }

      const response = await apiClient.post('/timeclock/clock-out', requestData)
      
      // Show success message
      setError(null)
      setScanResult(null)
      onClockAction()
      
      // Show success alert
      alert(`✅ ${response.data.message}`)
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to clock out')
    } finally {
      setLoading(false)
    }
  }

  const handleStartBreak = async () => {
    if (!activeTimeEntry) return

    setLoading(true)
    setError(null)

    try {
      const response = await apiClient.post('/timeclock/break', {
        time_entry_id: activeTimeEntry.id,
        action: 'start'
      })
      
      alert(`✅ ${response.data.message}`)
      onClockAction()
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to start break')
    } finally {
      setLoading(false)
    }
  }

  const handleEndBreak = async () => {
    if (!activeTimeEntry) return

    setLoading(true)
    setError(null)

    try {
      const response = await apiClient.post('/timeclock/break', {
        time_entry_id: activeTimeEntry.id,
        action: 'end'
      })
      
      alert(`✅ ${response.data.message}`)
      onClockAction()
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to end break')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Scanner Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <QrCode className="w-5 h-5" />
            QR Code Scanner
          </CardTitle>
          <CardDescription>
            Scan a job site QR code to clock in or out
          </CardDescription>
        </CardHeader>
        <CardContent>
          {error && (
            <Alert className="mb-4" variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {!isScanning && !scanResult && (
            <div className="text-center py-8">
              <Camera className="w-16 h-16 mx-auto text-gray-400 mb-4" />
              <p className="text-gray-600 mb-4">
                Ready to scan QR code
              </p>
              <Button onClick={startScanner} className="flex items-center gap-2">
                <Camera className="w-4 h-4" />
                Start Camera
              </Button>
            </div>
          )}

          {isScanning && (
            <div className="space-y-4">
              <div id={elementId} className="w-full"></div>
              <div className="text-center">
                <Button variant="outline" onClick={stopScanner}>
                  Stop Scanner
                </Button>
              </div>
            </div>
          )}

          {loading && (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Processing...</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Scan Result Card */}
      {scanResult && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MapPin className="w-5 h-5" />
              {scanResult.job_site.name}
            </CardTitle>
            {scanResult.job_site.address && (
              <CardDescription>{scanResult.job_site.address}</CardDescription>
            )}
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <Alert>
                <CheckCircle className="h-4 w-4" />
                <AlertDescription>{scanResult.message}</AlertDescription>
              </Alert>

              {scanResult.job_site.description && (
                <p className="text-sm text-gray-600">
                  {scanResult.job_site.description}
                </p>
              )}

              <div className="flex gap-2 flex-wrap">
                {scanResult.can_clock_in && (
                  <Button 
                    onClick={handleClockIn}
                    disabled={loading}
                    className="flex items-center gap-2"
                  >
                    <Clock className="w-4 h-4" />
                    Clock In
                  </Button>
                )}

                {scanResult.can_clock_out && (
                  <Button 
                    onClick={handleClockOut}
                    disabled={loading}
                    variant="outline"
                    className="flex items-center gap-2"
                  >
                    <LogOut className="w-4 h-4" />
                    Clock Out
                  </Button>
                )}

                <Button 
                  variant="ghost" 
                  onClick={() => setScanResult(null)}
                  className="ml-auto"
                >
                  Cancel
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Break Controls */}
      {activeTimeEntry && !scanResult && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Coffee className="w-5 h-5" />
              Break Controls
            </CardTitle>
            <CardDescription>
              Manage your break time
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-2">
              <Button 
                onClick={handleStartBreak}
                disabled={loading}
                variant="outline"
                className="flex items-center gap-2"
              >
                <Coffee className="w-4 h-4" />
                Start Break
              </Button>
              <Button 
                onClick={handleEndBreak}
                disabled={loading}
                variant="outline"
                className="flex items-center gap-2"
              >
                <Clock className="w-4 h-4" />
                End Break
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Location Status */}
      <div className="text-xs text-gray-500 text-center">
        {location ? (
          <span className="flex items-center justify-center gap-1">
            <MapPin className="w-3 h-3" />
            Location enabled for geofencing
          </span>
        ) : (
          <span className="flex items-center justify-center gap-1">
            <AlertCircle className="w-3 h-3" />
            Location access denied - geofencing disabled
          </span>
        )}
      </div>
    </div>
  )
}
