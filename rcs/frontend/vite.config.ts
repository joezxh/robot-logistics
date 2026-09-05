/// <reference types="vitest" />
import { fileURLToPath, URL } from 'node:url'
import { readFileSync, existsSync } from 'node:fs'
import { extname, join, normalize } from 'node:path'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Dev-only static server for MuJoCo robot assets (MJCF + OBJ meshes) so the
// MjcfLoader can fetch them from the repo without a backend endpoint. Serves
// /sim-assets/* from <repo>/simulation/backend/assets/*.
const SIM_ASSETS_ROOT = fileURLToPath(new URL('../../simulation/backend/assets', import.meta.url))
const MIME: Record<string, string> = {
  '.xml': 'application/xml',
  '.obj': 'text/plain',
  '.mtl': 'text/plain',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.stl': 'model/stl',
  '.json': 'application/json',
}

export default defineConfig({
  plugins: [vue()],
  // `@mujoco/mujoco` is an Emscripten WASM module; letting Vite pre-bundle it
  // breaks its relative wasm lookup. Exclude it so it is loaded as-is and the
  // browser fetches mujoco.wasm from node_modules at runtime.
  optimizeDeps: {
    exclude: ['@mujoco/mujoco'],
  },
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
      // Microduck SSE qpos stream (stdlib server, see rcs_env/serve/sse_qpos.py).
      '/sim': {
        target: 'http://localhost:8110',
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
    configureServer(server) {
      server.middlewares.use('/sim-assets', (req, res, next) => {
        const rel = normalize(decodeURIComponent(req.url || '/')).replace(/^(\.\.[/\\])+/, '')
        const full = join(SIM_ASSETS_ROOT, rel)
        if (!full.startsWith(SIM_ASSETS_ROOT) || !existsSync(full)) {
          res.statusCode = 404
          res.end('not found')
          return
        }
        try {
          const buf = readFileSync(full)
          res.setHeader('Content-Type', MIME[extname(full).toLowerCase()] || 'application/octet-stream')
          res.setHeader('Access-Control-Allow-Origin', '*')
          res.end(buf)
        } catch {
          res.statusCode = 500
          res.end('read error')
        }
      })
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    include: ['src/**/*.spec.ts'],
  },
})
