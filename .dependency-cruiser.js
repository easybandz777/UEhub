/** @type {import('dependency-cruiser').IConfiguration} */
module.exports = {
  forbidden: [
    {
      name: 'no-circular',
      severity: 'error',
      comment: 'Circular dependencies are not allowed',
      from: {},
      to: {
        circular: true
      }
    },
    {
      name: 'no-orphans',
      severity: 'warn',
      comment: 'Orphan modules should be avoided',
      from: {
        orphan: true,
        pathNot: [
          '(^|/)\\.[^/]+\\.(js|cjs|mjs|ts|json)$', // dot files
          '\\.d\\.ts$',                              // TypeScript declaration files
          '(^|/)tsconfig\\.json$',                   // TypeScript config
          '(^|/)(babel|webpack)\\.config\\.(js|cjs|mjs|ts|json)$' // configs
        ]
      },
      to: {}
    },
    {
      name: 'backend-module-boundaries',
      severity: 'error',
      comment: 'Backend modules should not import each other directly',
      from: {
        path: '^backend/app/modules/[^/]+/(?!__init__|events)',
      },
      to: {
        path: '^backend/app/modules/[^/]+/',
        pathNot: [
          '^backend/app/core/',
          '^backend/app/modules/[^/]+/events\\.py$'
        ]
      }
    },
    {
      name: 'frontend-feature-boundaries',
      severity: 'error',
      comment: 'Frontend features should only import from core and shared packages',
      from: {
        path: '^frontend/src/features/(?!core)',
      },
      to: {
        path: '^frontend/src/features/(?!core)',
        pathNot: [
          '^packages/',
          '^frontend/src/lib/',
          '^@ue-hub/'
        ]
      }
    }
  ],
  options: {
    doNotFollow: {
      path: 'node_modules'
    },
    exclude: {
      path: [
        'node_modules',
        '\\.d\\.ts$',
        'coverage',
        'dist',
        'build',
        '\\.next'
      ]
    },
    tsPreCompilationDeps: true,
    tsConfig: {
      fileName: 'tsconfig.json'
    },
    enhancedResolveOptions: {
      exportsFields: ['exports'],
      conditionNames: ['import', 'require', 'node', 'default']
    },
    reporterOptions: {
      dot: {
        collapsePattern: 'node_modules/(@[^/]+/[^/]+|[^/]+)'
      }
    }
  }
}
