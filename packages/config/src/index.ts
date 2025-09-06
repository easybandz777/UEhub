import { z } from 'zod'

// Environment configuration schemas
export const DatabaseConfigSchema = z.object({
  url: z.string().url(),
  ssl: z.boolean().default(true),
  pool_size: z.number().default(10),
  max_overflow: z.number().default(20),
})

export const RedisConfigSchema = z.object({
  url: z.string().url(),
  db: z.number().default(0),
  max_connections: z.number().default(10),
})

export const AuthConfigSchema = z.object({
  secret_key: z.string().min(32),
  algorithm: z.string().default('HS256'),
  access_token_expire_minutes: z.number().default(30),
  refresh_token_expire_days: z.number().default(7),
})

export const StorageConfigSchema = z.object({
  backend: z.enum(['local', 's3']).default('local'),
  local_path: z.string().default('./uploads'),
  s3_bucket: z.string().optional(),
  s3_region: z.string().optional(),
  s3_access_key: z.string().optional(),
  s3_secret_key: z.string().optional(),
})

export const MailConfigSchema = z.object({
  backend: z.enum(['console', 'resend']).default('console'),
  resend_api_key: z.string().optional(),
  from_email: z.string().email().default('noreply@uehub.com'),
  from_name: z.string().default('UE Hub'),
})

export const AppConfigSchema = z.object({
  name: z.string().default('UE Hub'),
  version: z.string().default('1.0.0'),
  environment: z.enum(['development', 'staging', 'production']).default('development'),
  debug: z.boolean().default(false),
  cors_origins: z.array(z.string()).default(['http://localhost:3000']),
  sentry_dsn: z.string().optional(),
})

// Combined configuration schema
export const ConfigSchema = z.object({
  app: AppConfigSchema,
  database: DatabaseConfigSchema,
  redis: RedisConfigSchema,
  auth: AuthConfigSchema,
  storage: StorageConfigSchema,
  mail: MailConfigSchema,
})

export type Config = z.infer<typeof ConfigSchema>
export type DatabaseConfig = z.infer<typeof DatabaseConfigSchema>
export type RedisConfig = z.infer<typeof RedisConfigSchema>
export type AuthConfig = z.infer<typeof AuthConfigSchema>
export type StorageConfig = z.infer<typeof StorageConfigSchema>
export type MailConfig = z.infer<typeof MailConfigSchema>
export type AppConfig = z.infer<typeof AppConfigSchema>

// Environment variable parsing utilities
export function parseEnvVar(key: string, defaultValue?: string): string {
  const value = process.env[key]
  if (value === undefined) {
    if (defaultValue !== undefined) {
      return defaultValue
    }
    throw new Error(`Environment variable ${key} is required`)
  }
  return value
}

export function parseEnvVarInt(key: string, defaultValue?: number): number {
  const value = process.env[key]
  if (value === undefined) {
    if (defaultValue !== undefined) {
      return defaultValue
    }
    throw new Error(`Environment variable ${key} is required`)
  }
  const parsed = parseInt(value, 10)
  if (isNaN(parsed)) {
    throw new Error(`Environment variable ${key} must be a valid integer`)
  }
  return parsed
}

export function parseEnvVarBool(key: string, defaultValue?: boolean): boolean {
  const value = process.env[key]
  if (value === undefined) {
    if (defaultValue !== undefined) {
      return defaultValue
    }
    throw new Error(`Environment variable ${key} is required`)
  }
  return value.toLowerCase() === 'true'
}

export function parseEnvVarArray(key: string, separator = ',', defaultValue?: string[]): string[] {
  const value = process.env[key]
  if (value === undefined) {
    if (defaultValue !== undefined) {
      return defaultValue
    }
    throw new Error(`Environment variable ${key} is required`)
  }
  return value.split(separator).map(s => s.trim()).filter(s => s.length > 0)
}

// Configuration factory
export function createConfig(): Config {
  const config = {
    app: {
      name: parseEnvVar('APP_NAME', 'UE Hub'),
      version: parseEnvVar('APP_VERSION', '1.0.0'),
      environment: parseEnvVar('NODE_ENV', 'development') as 'development' | 'staging' | 'production',
      debug: parseEnvVarBool('DEBUG', false),
      cors_origins: parseEnvVarArray('CORS_ORIGINS', ',', ['http://localhost:3000']),
      sentry_dsn: process.env.SENTRY_DSN,
    },
    database: {
      url: parseEnvVar('DATABASE_URL'),
      ssl: parseEnvVarBool('DATABASE_SSL', true),
      pool_size: parseEnvVarInt('DATABASE_POOL_SIZE', 10),
      max_overflow: parseEnvVarInt('DATABASE_MAX_OVERFLOW', 20),
    },
    redis: {
      url: parseEnvVar('REDIS_URL'),
      db: parseEnvVarInt('REDIS_DB', 0),
      max_connections: parseEnvVarInt('REDIS_MAX_CONNECTIONS', 10),
    },
    auth: {
      secret_key: parseEnvVar('SECRET_KEY'),
      algorithm: parseEnvVar('JWT_ALGORITHM', 'HS256'),
      access_token_expire_minutes: parseEnvVarInt('ACCESS_TOKEN_EXPIRE_MINUTES', 30),
      refresh_token_expire_days: parseEnvVarInt('REFRESH_TOKEN_EXPIRE_DAYS', 7),
    },
    storage: {
      backend: parseEnvVar('STORAGE_BACKEND', 'local') as 'local' | 's3',
      local_path: parseEnvVar('STORAGE_LOCAL_PATH', './uploads'),
      s3_bucket: process.env.S3_BUCKET,
      s3_region: process.env.S3_REGION,
      s3_access_key: process.env.S3_ACCESS_KEY,
      s3_secret_key: process.env.S3_SECRET_KEY,
    },
    mail: {
      backend: parseEnvVar('MAIL_BACKEND', 'console') as 'console' | 'resend',
      resend_api_key: process.env.RESEND_API_KEY,
      from_email: parseEnvVar('MAIL_FROM_EMAIL', 'noreply@uehub.com'),
      from_name: parseEnvVar('MAIL_FROM_NAME', 'UE Hub'),
    },
  }

  return ConfigSchema.parse(config)
}

// Feature flag utilities
export interface FeatureFlag {
  key: string
  enabled: boolean
  payload: Record<string, any>
}

export class FeatureFlagManager {
  private flags: Map<string, FeatureFlag> = new Map()

  setFlag(key: string, enabled: boolean, payload: Record<string, any> = {}): void {
    this.flags.set(key, { key, enabled, payload })
  }

  isEnabled(key: string): boolean {
    const flag = this.flags.get(key)
    return flag?.enabled ?? false
  }

  getPayload(key: string): Record<string, any> {
    const flag = this.flags.get(key)
    return flag?.payload ?? {}
  }

  getAllFlags(): FeatureFlag[] {
    return Array.from(this.flags.values())
  }

  loadFromObject(flags: Record<string, { enabled: boolean; payload?: Record<string, any> }>): void {
    Object.entries(flags).forEach(([key, config]) => {
      this.setFlag(key, config.enabled, config.payload ?? {})
    })
  }
}
