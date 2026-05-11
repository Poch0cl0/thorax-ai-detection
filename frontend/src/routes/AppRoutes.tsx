import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider } from '../context/AuthProvider'
import { AppLayout } from '../components/layout/AppLayout'
import { ProtectedRoute } from './ProtectedRoute'
import { RoleGate } from '../components/layout/RoleGate'
import { DashboardPage } from '../pages/DashboardPage'
import { LoginPage } from '../pages/LoginPage'
import { PatientsPage } from '../pages/PatientsPage'
import { PredictionsPage } from '../pages/PredictionsPage'
import { StudiesPage } from '../pages/StudiesPage'
import { AppointmentsPage } from '../pages/AppointmentsPage'
import { AttendQueuePage } from '../pages/AttendQueuePage'
import { ScanPage } from '../pages/ScanPage'

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
            <Route
              path="/patients"
              element={
                <RoleGate allow={['especialista', 'secretaria', 'admin']}>
                  <PatientsPage />
                </RoleGate>
              }
            />
            <Route
              path="/predictions"
              element={
                <RoleGate allow={['especialista', 'admin']}>
                  <PredictionsPage />
                </RoleGate>
              }
            />
            <Route
              path="/attend-queue"
              element={
                <RoleGate allow={['especialista', 'admin']}>
                  <AttendQueuePage />
                </RoleGate>
              }
            />
            <Route
              path="/appointments"
              element={
                <RoleGate allow={['secretaria', 'admin']}>
                  <AppointmentsPage />
                </RoleGate>
              }
            />
            <Route path="/studies" element={<StudiesPage />} />
            <Route path="/predict" element={<Navigate to="/predictions" replace />} />
            <Route
              path="/scan"
              element={
                <RoleGate allow={['admin']}>
                  <ScanPage />
                </RoleGate>
              }
            />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
