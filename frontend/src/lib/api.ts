/**
 * API client for UE Hub backend
 * Uses XHR for POST requests to avoid fetch recursion issues
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api'
const DIRECT_API_URL = 'https://uehub.fly.dev/v1'

export interface InventoryItem {
  id: string
  sku: string
  name: string
  location: string
  barcode?: string
  qty: number
  min_qty: number
  is_low_stock: boolean
  updated_at: string
}

export interface InventoryStats {
  total_items: number
  total_value: number
  low_stock_count: number
  out_of_stock_count: number
  recent_movements: number
}

export interface InventoryListResponse {
  items: InventoryItem[]
  total: number
  page: number
  per_page: number
  pages: number
  stats?: InventoryStats
}

export interface CreateInventoryItem {
  sku: string
  name: string
  location: string
  barcode?: string
  qty: number
  min_qty: number
}

export interface UpdateInventoryItem {
  sku?: string
  name?: string
  location?: string
  barcode?: string
  min_qty?: number
}

class ApiClient {
  private baseUrl: string
  private token: string | null = null

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  setToken(token: string) {
    this.token = token
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    // Add any custom headers from options
    if (options.headers) {
      if (Array.isArray(options.headers)) {
        // Handle array format
        options.headers.forEach(([key, value]) => {
          headers[key] = value
        })
      } else {
        // Handle object format
        Object.entries(options.headers).forEach(([key, value]) => {
          headers[key] = value
        })
      }
    }

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`
    }

    const response = await fetch(url, {
      ...options,
      headers,
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`API Error: ${response.status} - ${errorText}`)
    }

    return response.json()
  }

  private async xhrRequest<T>(
    endpoint: string,
    options: {
      method?: string
      body?: string
      headers?: Record<string, string>
    } = {}
  ): Promise<T> {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest()
      const url = `${DIRECT_API_URL}${endpoint}`
      
      console.log('XHR Request:', options.method || 'GET', url)
      
      xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
          console.log('XHR Response:', xhr.status, xhr.responseText)
          
          if (xhr.status >= 200 && xhr.status < 300) {
            try {
              const result = JSON.parse(xhr.responseText)
              resolve(result)
            } catch (parseError) {
              reject(new Error(`Parse error: ${parseError}`))
            }
          } else {
            reject(new Error(`XHR Error: ${xhr.status} - ${xhr.responseText}`))
          }
        }
      }
      
      xhr.onerror = function() {
        reject(new Error('XHR Network Error'))
      }
      
      xhr.open(options.method || 'GET', url, true)
      
      // Set headers
      xhr.setRequestHeader('Content-Type', 'application/json')
      xhr.setRequestHeader('Accept', 'application/json')
      
      if (options.headers) {
        Object.entries(options.headers).forEach(([key, value]) => {
          xhr.setRequestHeader(key, value)
        })
      }
      
      if (this.token) {
        xhr.setRequestHeader('Authorization', `Bearer ${this.token}`)
      }
      
      xhr.send(options.body || null)
    })
  }

  // Inventory endpoints
  async getInventoryItems(params?: {
    page?: number
    per_page?: number
    search?: string
    location?: string
    low_stock_only?: boolean
    out_of_stock_only?: boolean
  }): Promise<InventoryListResponse> {
    const searchParams = new URLSearchParams()
    
    if (params?.page) searchParams.set('page', params.page.toString())
    if (params?.per_page) searchParams.set('per_page', params.per_page.toString())
    if (params?.search) searchParams.set('search', params.search)
    if (params?.location) searchParams.set('location', params.location)
    if (params?.low_stock_only) searchParams.set('low_stock_only', 'true')
    if (params?.out_of_stock_only) searchParams.set('out_of_stock_only', 'true')

    const query = searchParams.toString()
    const endpoint = `/inventory${query ? `?${query}` : ''}`
    
    return this.request<InventoryListResponse>(endpoint)
  }

  async getInventoryStats(): Promise<InventoryStats> {
    return this.request<InventoryStats>('/inventory/stats')
  }

  async getInventoryItem(id: string): Promise<InventoryItem> {
    return this.request<InventoryItem>(`/inventory/${id}`)
  }

  async createInventoryItem(item: CreateInventoryItem): Promise<InventoryItem> {
    // Use XHR for POST requests to avoid fetch recursion issues
    return this.xhrRequest<InventoryItem>('/inventory/', {
      method: 'POST',
      body: JSON.stringify(item),
    })
  }

  async updateInventoryItem(id: string, item: UpdateInventoryItem): Promise<InventoryItem> {
    return this.xhrRequest<InventoryItem>(`/inventory/${id}`, {
      method: 'PUT',
      body: JSON.stringify(item),
    })
  }

  async deleteInventoryItem(id: string): Promise<void> {
    await this.xhrRequest<void>(`/inventory/${id}`, {
      method: 'DELETE',
    })
  }

  async adjustInventoryQuantity(
    id: string,
    qty: number,
    reason: string,
    meta?: Record<string, any>
  ): Promise<InventoryItem> {
    return this.xhrRequest<InventoryItem>(`/inventory/${id}/adjust`, {
      method: 'POST',
      body: JSON.stringify({ qty, reason, meta }),
    })
  }

  async moveInventoryQuantity(
    id: string,
    delta: number,
    reason: string,
    meta?: Record<string, any>
  ): Promise<InventoryItem> {
    return this.xhrRequest<InventoryItem>(`/inventory/${id}/move`, {
      method: 'POST',
      body: JSON.stringify({ delta, reason, meta }),
    })
  }

  async searchByBarcode(barcode: string): Promise<{ item: InventoryItem | null; found: boolean }> {
    return this.request<{ item: InventoryItem | null; found: boolean }>(`/inventory/search/barcode/${barcode}`)
  }

  // Health check
  async healthCheck(): Promise<any> {
    return this.request('/health')
  }
}

export const apiClient = new ApiClient()
export default apiClient
