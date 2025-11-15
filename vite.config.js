import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  base: '/',
  plugins: [react()],
  build: {
    minify: 'esbuild',
    rollupOptions: {
      output: {
        manualChunks: undefined,
      }
    }
  },
  esbuild: {
    // 本番ビルドでconsole.logを削除
    drop: process.env.NODE_ENV === 'production' ? ['console', 'debugger'] : [],
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    open: false,
    strictPort: false,
    allowedHosts: [
      'unacquainted-superstrong-marley.ngrok-free.dev',
      'localhost',
      '127.0.0.1'
    ],
    middlewareMode: false,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        rewrite: (path) => path
      }
    }
  }
})
