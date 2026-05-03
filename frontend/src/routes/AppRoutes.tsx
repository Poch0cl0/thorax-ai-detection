import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider } from '../context/AuthProvider'
import { AppLayout } from '../components/layout/AppLayout'
import { ProtectedRoute } from './ProtectedRoute'
import { DashboardPage } from '../pages/DashboardPage'
import { LoginPage } from '../pages/LoginPage'
import { PatientsPage } from '../pages/PatientsPage'
import { PredictPage } from '../pages/PredictPage'
import { ScanPage } from '../pages/ScanPage'
import { StudiesPage } from '../pages/StudiesPage'

export function AppRoutes() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          >
            <Route path="/" element={<DashboardPage />} />
            <Route path="/patients" element={<PatientsPage />} />
            <Route path="/studies" element={<StudiesPage />} />
            <Route path="/predict" element={<PredictPage />} />
            <Route path="/scan" element={<ScanPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
