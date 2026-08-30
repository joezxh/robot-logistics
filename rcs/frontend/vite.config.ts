/// <reference types="vitest" />
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api/sys': {
        target: 'http://localhost:8100',
        changeOrigin: true,
      },
      '/api/rcs': {
        target: 'http://localhost:8100',
        changeOrigin: true,
      },
      // Simulation backend. MUST stay last: Vite matches proxy keys in
      // declaration order, and /api/rcs + /api/sys above belong to RCS.
      // Everything else under /api (tasks, devices, scenes, warehouse, plus the
      // SSE streams) is served by the simulation service.
      '/api': {
        target: process.env.VITE_SIM_API || 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    include: ['src/**/*.spec.ts'],
  },
})
