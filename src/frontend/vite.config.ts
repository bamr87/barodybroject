import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

// Django serves the built bundle from STATIC_URL + "frontend/", and reads
// dist/.vite/manifest.json to emit the hashed <script>/<link> tags
// (see parodynews/views/spa.py). In dev, Vite serves the app itself and
// proxies everything Django owns so cookies stay same-origin.
const DJANGO = process.env.DJANGO_ORIGIN ?? 'http://localhost:8000'
const proxied = ['/api', '/accounts', '/admin', '/setup', '/media', '/martor', '/i18n']

export default defineConfig({
  plugins: [react()],
  base: '/static/frontend/',
  build: {
    manifest: true,
    outDir: 'dist',
    emptyOutDir: true,
    rollupOptions: { input: 'src/main.tsx' },
  },
  server: {
    port: 5173,
    strictPort: true,
    proxy: Object.fromEntries(
      proxied.map((path) => [path, { target: DJANGO, changeOrigin: false }]),
    ),
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    css: false,
  },
})
