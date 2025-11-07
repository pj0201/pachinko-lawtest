import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import './index.css'
import App from './App.jsx'

// ✅ Capacitor Android 戻るボタン処理
if (window.Capacitor) {
  const { App: CapacitorApp } = window.Capacitor.Plugins;

  CapacitorApp?.addListener('backButton', ({ canGoBack }) => {
    if (!canGoBack) {
      // ホーム画面で戻るボタン → アプリ終了
      CapacitorApp?.exitApp?.();
    } else {
      // その他の画面で戻るボタン → ブラウザバック
      window.history.back();
    }
  });
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>,
)
