import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    port: 3004,
    proxy: {
      '/api': 'http://localhost:5004'  // Proxy backend APIs
    }
  },
  build: {
    outDir: 'dist'
  }
})