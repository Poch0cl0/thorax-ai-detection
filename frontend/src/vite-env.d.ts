/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string
  readonly VITE_USE_CLINICAL_MOCK?: string
  readonly VITE_SKIP_AUTH?: string
  readonly VITE_DEMO_LOGIN_EMAIL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
