import type { paths } from '@ue-hub/types'

export interface ApiClientConfig {
  baseUrl: string
  apiKey?: string
  timeout?: number
}

export class ApiClient {
  private baseUrl: string
  private apiKey?: string
  private timeout: number

  constructor(config: ApiClientConfig) {
    this.baseUrl = config.baseUrl.replace(/\/$/, '')
    this.apiKey = config.apiKey
    this.timeout = config.timeout || 10000
  }

  private async request<T>(
    method: string,
    path: string,
    options: {
      body?: any
      params?: Record<string, any>
      headers?: Record<string, string>
    } = {}
  ): Promise<T> {
    const url = new URL(path, this.baseUrl)
    
    if (options.params) {
      Object.entries(options.params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          url.searchParams.append(key, String(value))
        }
      })
    }

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...options.headers,
    }

    if (this.apiKey) {
      headers.Authorization = `Bearer ${this.apiKey}`
    }

    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), this.timeout)

    try {
      const response = await fetch(url.toString(), {
        method,
        headers,
        body: options.body ? JSON.stringify(options.body) : undefined,
        signal: controller.signal,
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
        throw new ApiError(response.status, error.detail || 'Request failed', error)
      }

      return await response.json()
    } catch (error) {
      clearTimeout(timeoutId)
      if (error instanceof ApiError) {
        throw error
      }
      throw new ApiError(0, 'Network error', { detail: String(error) })
    }
  }

  // Auth endpoints
  async login(email: string, password: string) {
    return this.request<{
      access_token: string
      token_type: string
      user: {
        id: string
        email: string
        name: string
        role: string
      }
    }>('POST', '/v1/auth/login', {
      body: { email, password }
    })
  }

  async getCurrentUser() {
    return this.request<{
      id: string
      email: string
      name: string
      role: string
      created_at: string
    }>('GET', '/v1/auth/me')
  }

  // Inventory endpoints
  async getInventoryItems(params?: {
    page?: number
    per_page?: number
    search?: string
  }) {
    return this.request<{
      items: Array<{
        id: string
        sku: string
        name: string
        qty: number
        location: string
        barcode?: string
        min_qty: number
        updated_at: string
      }>
      total: number
      page: number
      per_page: number
      pages: number
    }>('GET', '/v1/inventory/items', { params })
  }

  async createInventoryItem(data: {
    sku: string
    name: string
    qty: number
    location: string
    barcode?: string
    min_qty: number
  }) {
    return this.request<{
      id: string
      sku: string
      name: string
      qty: number
      location: string
      barcode?: string
      min_qty: number
      updated_at: string
    }>('POST', '/v1/inventory/items', { body: data })
  }

  async getInventoryItem(id: string) {
    return this.request<{
      id: string
      sku: string
      name: string
      qty: number
      location: string
      barcode?: string
      min_qty: number
      updated_at: string
    }>('GET', `/v1/inventory/items/${id}`)
  }

  async updateInventoryItem(id: string, data: Partial<{
    sku: string
    name: string
    qty: number
    location: string
    barcode?: string
    min_qty: number
  }>) {
    return this.request<{
      id: string
      sku: string
      name: string
      qty: number
      location: string
      barcode?: string
      min_qty: number
      updated_at: string
    }>('PUT', `/v1/inventory/items/${id}`, { body: data })
  }

  async deleteInventoryItem(id: string) {
    return this.request<{ message: string }>('DELETE', `/v1/inventory/items/${id}`)
  }

  // Training endpoints
  async getTrainingModules(params?: {
    page?: number
    per_page?: number
    active?: boolean
  }) {
    return this.request<{
      items: Array<{
        id: string
        title: string
        version: number
        content_url: string
        duration_min: number
        active: boolean
      }>
      total: number
      page: number
      per_page: number
      pages: number
    }>('GET', '/v1/training/modules', { params })
  }

  async startTrainingAttempt(moduleId: string) {
    return this.request<{
      id: string
      user_id: string
      module_id: string
      started_at: string
    }>('POST', `/v1/training/modules/${moduleId}/attempts`)
  }

  async submitTrainingAttempt(attemptId: string, data: {
    score: number
    xapi_data?: Record<string, any>
  }) {
    return this.request<{
      id: string
      user_id: string
      module_id: string
      score: number
      passed: boolean
      started_at: string
      completed_at: string
      xapi_json: Record<string, any>
    }>('POST', `/v1/training/attempts/${attemptId}/submit`, { body: data })
  }

  // Feature flags
  async getFeatureFlags() {
    return this.request<Record<string, {
      enabled: boolean
      payload: Record<string, any>
    }>>('GET', '/v1/core/feature-flags')
  }
}

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public data?: any
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

// Default client instance
let defaultClient: ApiClient | null = null

export function createApiClient(config: ApiClientConfig): ApiClient {
  return new ApiClient(config)
}

export function setDefaultApiClient(client: ApiClient): void {
  defaultClient = client
}

export function getDefaultApiClient(): ApiClient {
  if (!defaultClient) {
    throw new Error('No default API client configured. Call setDefaultApiClient() first.')
  }
  return defaultClient
}

// Re-export types
export type * from '@ue-hub/types'
