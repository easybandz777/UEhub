// Generated API types
export type * from './api'

// Common shared types
export interface User {
  id: string
  email: string
  name: string
  role: 'admin' | 'manager' | 'worker'
  created_at: string
}

export interface FeatureFlag {
  key: string
  enabled: boolean
  payload: Record<string, any>
  updated_at: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  pages: number
}

export interface ApiError {
  detail: string
  code?: string
  field?: string
}

// Domain-specific types
export interface InventoryItem {
  id: string
  sku: string
  name: string
  qty: number
  location: string
  barcode?: string
  min_qty: number
  updated_at: string
}

export interface InventoryEvent {
  id: string
  item_id: string
  delta: number
  reason: string
  actor_id: string
  meta_json: Record<string, any>
  created_at: string
}

export interface TrainingModule {
  id: string
  title: string
  version: number
  content_url: string
  duration_min: number
  active: boolean
}

export interface TrainingAttempt {
  id: string
  user_id: string
  module_id: string
  score: number
  passed: boolean
  started_at: string
  completed_at?: string
  xapi_json: Record<string, any>
}

export interface Certificate {
  id: string
  attempt_id: string
  pdf_url: string
  issued_at: string
  hash: string
}

export interface OutboundWebhook {
  id: string
  kind: string
  target_url: string
  secret: string
  active: boolean
  created_at: string
}
