module.exports = {
  extends: [
    'next/core-web-vitals',
    '@typescript-eslint/recommended',
  ],
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint', 'import'],
  rules: {
    // Import rules for module boundaries
    'import/no-restricted-paths': [
      'error',
      {
        zones: [
          // Backend module boundaries
          {
            target: './backend/app/modules/*/!(router|schemas).py',
            from: './backend/app/modules/*/!(events).py',
            except: ['./backend/app/core/**'],
            message: 'Modules should not import each other\'s internals. Use events or shared interfaces.',
          },
          // Frontend feature boundaries
          {
            target: './frontend/src/features/*/!(core)/**',
            from: './frontend/src/features/*/!(core)/**',
            except: [
              './frontend/src/features/core/**',
              './packages/**',
            ],
            message: 'Features should only import from core feature and shared packages.',
          },
        ],
      },
    ],
    
    // TypeScript rules
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    '@typescript-eslint/no-explicit-any': 'warn',
    '@typescript-eslint/prefer-const': 'error',
    '@typescript-eslint/no-non-null-assertion': 'warn',
    
    // General rules
    'no-console': ['warn', { allow: ['warn', 'error'] }],
    'prefer-const': 'error',
    'no-var': 'error',
    
    // Import organization
    'import/order': [
      'error',
      {
        groups: [
          'builtin',
          'external',
          'internal',
          'parent',
          'sibling',
          'index',
        ],
        'newlines-between': 'always',
        alphabetize: {
          order: 'asc',
          caseInsensitive: true,
        },
      },
    ],
  },
  overrides: [
    {
      files: ['*.test.ts', '*.test.tsx', '*.spec.ts', '*.spec.tsx'],
      rules: {
        '@typescript-eslint/no-explicit-any': 'off',
        'import/no-restricted-paths': 'off',
      },
    },
  ],
}
