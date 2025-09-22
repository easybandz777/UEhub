const DIRECT_API_URL = '/api/v1'

// Types
export interface User {
  id: string
  email: string
  name: string
  role: 'superadmin' | 'admin' | 'employee'
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  name: string
  password: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: User
}

export interface InventoryItem {
  id: string
  sku: string
  name: string
  location: string
  barcode?: string
  min_qty: number
  qty: number
  is_low_stock: boolean
  updated_at: string
}

export interface InventoryItemCreate {
  sku: string
  name: string
  location: string
  barcode?: string
  min_qty: number
  qty: number
}

export interface InventoryStats {
  total_items: number
  total_value: number
  low_stock_count: number
  out_of_stock_count: number
  recent_movements: number
}

export interface SafetyChecklist {
  id: string
  project_name: string
  location: string
  inspector_id: string
  inspection_date: string
  scaffold_type: string
  height: string
  contractor?: string
  permit_number?: string
  status: 'draft' | 'completed' | 'approved'
  total_items: number
  passed_items: number
  failed_items: number
  na_items: number
  critical_failures: number
  approved_by_id?: string
  approved_at?: string
  created_at: string
  updated_at: string
  checklist_items: SafetyChecklistItem[]
}

export interface SafetyChecklistItem {
  id: string
  checklist_id: string
  item_id: string
  category: string
  number: string
  text: string
  is_critical: boolean
  status?: 'pass' | 'fail' | 'na'
  notes?: string
  created_at: string
  updated_at: string
}

export interface SafetyChecklistCreate {
  project_name: string
  location: string
  inspection_date: string
  scaffold_type: string
  height: string
  contractor?: string
  permit_number?: string
  checklist_items: Omit<SafetyChecklistItem, 'id' | 'checklist_id' | 'created_at' | 'updated_at'>[]
}

export interface SafetyStats {
  total_checklists: number
  completed_checklists: number
  approved_checklists: number
  pending_approval: number
  critical_failures_count: number
  average_completion_rate: number
  checklists_this_month: number
  checklists_this_week: number
}

// Auth storage
class AuthStorage {
  private static readonly ACCESS_TOKEN_KEY = 'access_token'
  private static readonly REFRESH_TOKEN_KEY = 'refresh_token'
  private static readonly USER_KEY = 'user'

  static getAccessToken(): string | null {
    if (typeof window === 'undefined') return null
    return localStorage.getItem(this.ACCESS_TOKEN_KEY)
  }

  static setAccessToken(token: string): void {
    if (typeof window === 'undefined') return
    localStorage.setItem(this.ACCESS_TOKEN_KEY, token)
  }

  static getRefreshToken(): string | null {
    if (typeof window === 'undefined') return null
    return localStorage.getItem(this.REFRESH_TOKEN_KEY)
  }

  static setRefreshToken(token: string): void {
    if (typeof window === 'undefined') return
    localStorage.setItem(this.REFRESH_TOKEN_KEY, token)
  }

  static getUser(): User | null {
    if (typeof window === 'undefined') return null
    const userStr = localStorage.getItem(this.USER_KEY)
    return userStr ? JSON.parse(userStr) : null
  }

  static setUser(user: User): void {
    if (typeof window === 'undefined') return
    localStorage.setItem(this.USER_KEY, JSON.stringify(user))
  }

  static clear(): void {
    if (typeof window === 'undefined') return
    localStorage.removeItem(this.ACCESS_TOKEN_KEY)
    localStorage.removeItem(this.REFRESH_TOKEN_KEY)
    localStorage.removeItem(this.USER_KEY)
  }
}

export class ApiClient {
  private baseUrl: string

  constructor() {
    this.baseUrl = DIRECT_API_URL
  }

  // Lightweight axios-like helpers returning { data }
  async get<T>(
    endpoint: string,
    options: { headers?: Record<string, string>; requireAuth?: boolean } = {}
  ): Promise<{ data: T }> {
    const data = await this.xhrRequest<T>(endpoint, {
      method: 'GET',
      headers: options.headers,
      requireAuth: options.requireAuth,
    })
    return { data }
  }

  async post<T>(
    endpoint: string,
    body?: unknown,
    options: { headers?: Record<string, string>; requireAuth?: boolean } = {}
  ): Promise<{ data: T }> {
    const data = await this.xhrRequest<T>(endpoint, {
      method: 'POST',
      body: body !== undefined ? JSON.stringify(body) : undefined,
      headers: options.headers,
      requireAuth: options.requireAuth,
    })
    return { data }
  }

  async put<T>(
    endpoint: string,
    body?: unknown,
    options: { headers?: Record<string, string>; requireAuth?: boolean } = {}
  ): Promise<{ data: T }> {
    const data = await this.xhrRequest<T>(endpoint, {
      method: 'PUT',
      body: body !== undefined ? JSON.stringify(body) : undefined,
      headers: options.headers,
      requireAuth: options.requireAuth,
    })
    return { data }
  }

  async delete<T>(
    endpoint: string,
    options: { headers?: Record<string, string>; requireAuth?: boolean } = {}
  ): Promise<{ data: T }> {
    const data = await this.xhrRequest<T>(endpoint, {
      method: 'DELETE',
      headers: options.headers,
      requireAuth: options.requireAuth,
    })
    return { data }
  }

  private async xhrRequest<T>(
    endpoint: string,
    options: {
      method?: string
      body?: string
      headers?: Record<string, string>
      requireAuth?: boolean
    } = {}
  ): Promise<T> {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest()
      const url = `${this.baseUrl}${endpoint}`
      const method = options.method || 'GET'

      xhr.open(method, url, true)

      // Set headers
      const headers: Record<string, string> = {
        'Accept': 'application/json',
        ...options.headers
      }

      // Add auth header if required
      if (options.requireAuth !== false) {
        const token = AuthStorage.getAccessToken()
        if (token) {
          headers['Authorization'] = `Bearer ${token}`
        }
      }

      // Set Content-Type for requests with body
      if (options.body && !headers['Content-Type']) {
        headers['Content-Type'] = 'application/json'
      }

      Object.keys(headers).forEach((key: string) => {
        xhr.setRequestHeader(key, headers[key])
      })

      xhr.onreadystatechange = () => {
        if (xhr.readyState === XMLHttpRequest.DONE) {
          if (xhr.status >= 200 && xhr.status < 300) {
            try {
              const response = xhr.responseText ? JSON.parse(xhr.responseText) : {}
              resolve(response)
            } catch (error) {
              reject(new Error('Failed to parse response'))
            }
          } else {
            try {
              const error = xhr.responseText ? JSON.parse(xhr.responseText) : { detail: 'Request failed' }
              reject(new Error(error.detail || `Request failed with status ${xhr.status}`))
            } catch {
              reject(new Error(`Request failed with status ${xhr.status}`))
            }
          }
        }
      }

      xhr.onerror = () => {
        reject(new Error('Network error'))
      }

      xhr.send(options.body)
    })
  }

  // Auth methods
  async register(data: RegisterRequest): Promise<User> {
    return this.xhrRequest<User>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
      requireAuth: false
    })
  }

  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await this.xhrRequest<LoginResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
      requireAuth: false
    })

    // Store tokens and user
    AuthStorage.setAccessToken(response.access_token)
    AuthStorage.setRefreshToken(response.refresh_token)
    AuthStorage.setUser(response.user)

    return response
  }

  async logout(): Promise<void> {
    AuthStorage.clear()
  }

  async getCurrentUser(): Promise<User> {
    return this.xhrRequest<User>('/auth/me')
  }

  async refreshToken(): Promise<void> {
    const refreshToken = AuthStorage.getRefreshToken()
    if (!refreshToken) {
      throw new Error('No refresh token available')
    }

    const response = await this.xhrRequest<{ access_token: string; expires_in: number }>('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
      requireAuth: false
    })

    AuthStorage.setAccessToken(response.access_token)
  }

  isAuthenticated(): boolean {
    return !!AuthStorage.getAccessToken()
  }

  getCurrentUserFromStorage(): User | null {
    return AuthStorage.getUser()
  }

  // Inventory methods (existing)
  async createInventoryItem(item: InventoryItemCreate): Promise<InventoryItem> {
    return this.xhrRequest<InventoryItem>('/inventory/', {
      method: 'POST',
      body: JSON.stringify(item)
    })
  }

  async updateInventoryItem(id: string, item: Partial<InventoryItem>): Promise<InventoryItem> {
    return this.xhrRequest<InventoryItem>(`/inventory/${id}`, {
      method: 'PUT',
      body: JSON.stringify(item)
    })
  }

  async deleteInventoryItem(id: string): Promise<void> {
    return this.xhrRequest<void>(`/inventory/${id}`, {
      method: 'DELETE'
    })
  }

  async adjustInventoryQuantity(id: string, adjustment: number, reason?: string): Promise<InventoryItem> {
    return this.xhrRequest<InventoryItem>(`/inventory/${id}/adjust`, {
      method: 'POST',
      body: JSON.stringify({ adjustment, reason })
    })
  }

  async moveInventoryQuantity(id: string, quantity: number, to_location: string, reason?: string): Promise<InventoryItem> {
    return this.xhrRequest<InventoryItem>(`/inventory/${id}/move`, {
      method: 'POST',
      body: JSON.stringify({ quantity, to_location, reason })
    })
  }

  async getInventoryItems(params?: {
    page?: number
    per_page?: number
    search?: string
    category?: string
    location?: string
    low_stock?: boolean
  }): Promise<{
    items: InventoryItem[]
    total: number
    page: number
    per_page: number
    pages: number
  }> {
    const searchParams = new URLSearchParams()
    if (params?.page) searchParams.append('page', params.page.toString())
    if (params?.per_page) searchParams.append('per_page', params.per_page.toString())
    if (params?.search) searchParams.append('search', params.search)
    if (params?.category) searchParams.append('category', params.category)
    if (params?.location) searchParams.append('location', params.location)
    if (params?.low_stock) searchParams.append('low_stock', 'true')

    const queryString = searchParams.toString()
    const endpoint = queryString ? `/inventory/?${queryString}` : '/inventory/'

    return this.xhrRequest(endpoint)
  }

  async getInventoryStats(): Promise<InventoryStats> {
    return this.xhrRequest<InventoryStats>('/inventory/stats')
  }

  async getInventoryItem(id: string): Promise<InventoryItem> {
    return this.xhrRequest<InventoryItem>(`/inventory/${id}`)
  }

  async searchByBarcode(barcode: string): Promise<InventoryItem | null> {
    return this.xhrRequest<InventoryItem | null>(`/inventory/barcode/${barcode}`)
  }

  // Safety checklist methods
  async createSafetyChecklist(data: SafetyChecklistCreate): Promise<SafetyChecklist> {
    return this.xhrRequest<SafetyChecklist>('/safety/checklists', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  async getSafetyChecklists(params?: {
    page?: number
    per_page?: number
    project_name?: string
    location?: string
    status?: string
    inspector_id?: string
    date_from?: string
    date_to?: string
    critical_failures_only?: boolean
  }): Promise<{
    items: SafetyChecklist[]
    total: number
    page: number
    per_page: number
    pages: number
  }> {
    const searchParams = new URLSearchParams()
    if (params?.page) searchParams.append('page', params.page.toString())
    if (params?.per_page) searchParams.append('per_page', params.per_page.toString())
    if (params?.project_name) searchParams.append('project_name', params.project_name)
    if (params?.location) searchParams.append('location', params.location)
    if (params?.status) searchParams.append('status', params.status)
    if (params?.inspector_id) searchParams.append('inspector_id', params.inspector_id)
    if (params?.date_from) searchParams.append('date_from', params.date_from)
    if (params?.date_to) searchParams.append('date_to', params.date_to)
    if (params?.critical_failures_only) searchParams.append('critical_failures_only', 'true')

    const queryString = searchParams.toString()
    const endpoint = queryString ? `/safety/checklists?${queryString}` : '/safety/checklists'

    return this.xhrRequest(endpoint)
  }

  async getSafetyChecklist(id: string): Promise<SafetyChecklist> {
    return this.xhrRequest<SafetyChecklist>(`/safety/checklists/${id}`)
  }

  async updateSafetyChecklist(id: string, data: Partial<SafetyChecklistCreate>): Promise<SafetyChecklist> {
    return this.xhrRequest<SafetyChecklist>(`/safety/checklists/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    })
  }

  async deleteSafetyChecklist(id: string): Promise<void> {
    return this.xhrRequest<void>(`/safety/checklists/${id}`, {
      method: 'DELETE'
    })
  }

  async updateChecklistItem(
    checklistId: string,
    itemId: string,
    data: { status?: 'pass' | 'fail' | 'na'; notes?: string }
  ): Promise<SafetyChecklistItem> {
    return this.xhrRequest<SafetyChecklistItem>(`/safety/checklists/${checklistId}/items/${itemId}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    })
  }

  async bulkUpdateChecklistItems(
    checklistId: string,
    updates: { item_id: string; status?: string; notes?: string }[]
  ): Promise<void> {
    return this.xhrRequest<void>(`/safety/checklists/${checklistId}/items/bulk-update`, {
      method: 'POST',
      body: JSON.stringify({ item_updates: updates })
    })
  }

  async approveChecklist(
    checklistId: string,
    approved: boolean,
    comments?: string
  ): Promise<SafetyChecklist> {
    return this.xhrRequest<SafetyChecklist>(`/safety/checklists/${checklistId}/approve`, {
      method: 'POST',
      body: JSON.stringify({ approved, comments })
    })
  }

  async getSafetyStats(): Promise<SafetyStats> {
    return this.xhrRequest<SafetyStats>('/safety/stats')
  }

  async getSafetyDashboard(): Promise<{
    stats: SafetyStats
    recent_checklists: SafetyChecklist[]
    pending_approvals: SafetyChecklist[]
    critical_failures: SafetyChecklist[]
    completion_trend: any[]
  }> {
    return this.xhrRequest('/safety/dashboard')
  }

  async getDefaultOSHATemplate(): Promise<any> {
    return this.xhrRequest('/safety/templates/default/osha')
  }

  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return this.xhrRequest('/health', { requireAuth: false })
  }
}

// Export singleton instance
export const apiClient = new ApiClient()
export { AuthStorage }