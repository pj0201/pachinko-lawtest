import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  base: '/',
  plugins: [react()],
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
      // ========================================
      // バックエンドAPIプロキシ設定（優先度順）
      // ========================================

      // 1. OCR処理 → Express (port 3001)
      '/api/ocr': {
        target: 'http://localhost:3001',
        changeOrigin: true,
        rewrite: (path) => path
      },
      '/api/pdf-ocr': {
        target: 'http://localhost:3001',
        changeOrigin: true,
        rewrite: (path) => path
      },

      // 2. データベース操作 → Express (port 3001)
      '/api/db': {
        target: 'http://localhost:3001',
        changeOrigin: true,
        rewrite: (path) => path
      },

      // 3. ログ取得 → Express (port 3001)
      '/api/logs': {
        target: 'http://localhost:3001',
        changeOrigin: true,
        rewrite: (path) => path
      },

      // 4. その他すべてのAPI（問題取得、認証等） → Flask (port 5000)
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        rewrite: (path) => path
      }
    }
  }
})
