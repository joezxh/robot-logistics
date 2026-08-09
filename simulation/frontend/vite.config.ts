import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      // When RCS runs standalone (RCS_EMBEDDED=0), point /api/rcs at it.
      // This entry must come first — Vite matches proxy keys in order.
      ...(process.env.VITE_RCS_STANDALONE === '1'
        ? {
            '/api/rcs': {
              target: process.env.VITE_RCS_URL || 'http://localhost:8100',
              ws: true
            }
          }
        : {}),
      '/api': 'http://localhost:8000',
      '/ws': { target: 'ws://localhost:8000', ws: true }
    }
  }
})