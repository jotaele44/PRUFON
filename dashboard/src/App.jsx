import React from 'react'
import { Toaster } from '@/components/ui/toaster'
import { QueryClientProvider } from '@tanstack/react-query'
import { queryClientInstance } from '@/lib/query-client'
import { BrowserRouter, HashRouter, Route, Routes } from 'react-router-dom'
import PageNotFound from './lib/PageNotFound'

// Standalone (file://) exports use HashRouter so "/" resolves without the History API.
const Router = import.meta.env.VITE_OFFLINE === '1' ? HashRouter : BrowserRouter
import ScrollToTop from './components/ScrollToTop'
import Dashboard from './pages/Dashboard'
import ErrorBoundary from './components/ErrorBoundary'

// Auth stripped: routes render directly, no AuthProvider / ProtectedRoute.
function App() {
  return (
    <QueryClientProvider client={queryClientInstance}>
      <Router>
        <ScrollToTop />
        {/* Inside the router so a throw keeps the shell and the URL, and the
            operator can navigate away instead of facing a blank document. */}
        <ErrorBoundary>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="*" element={<PageNotFound />} />
          </Routes>
        </ErrorBoundary>
      </Router>
      <Toaster />
    </QueryClientProvider>
  )
}

export default App
