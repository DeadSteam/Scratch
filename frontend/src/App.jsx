/**
 * Main Application Component
 * Routes and providers setup
 */

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@context/ThemeContext';
import { AuthProvider } from '@context/AuthContext';
import { NotificationProvider } from '@context/NotificationContext';
import { ProtectedRoute } from '@components/layout';
import { ToastContainer } from '@components/common';
import { ROUTES } from '@utils/constants';

// Pages
import LoginPage from '@pages/LoginPage';
import ExperimentsPage from '@pages/ExperimentsPage';
import CreateExperimentPage from '@pages/CreateExperimentPage';
import ExperimentDetailPage from '@pages/ExperimentDetailPage';
import AdminPage from '@pages/AdminPage';

// Styles
import '@styles/global.css';

export function App() {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <AuthProvider>
          <NotificationProvider>
          {/* Toast notifications */}
          <ToastContainer />
          
          {/* Routes */}
          <Routes>
            {/* Public routes */}
            <Route path={ROUTES.LOGIN} element={<LoginPage />} />
            
            {/* Protected routes */}
            <Route
              path={ROUTES.EXPERIMENTS}
              element={
                <ProtectedRoute>
                  <ExperimentsPage />
                </ProtectedRoute>
              }
            />
            
            <Route
              path={ROUTES.EXPERIMENT_NEW}
              element={
                <ProtectedRoute>
                  <CreateExperimentPage />
                </ProtectedRoute>
              }
            />
            
            <Route
              path={ROUTES.EXPERIMENT_DETAIL}
              element={
                <ProtectedRoute>
                  <ExperimentDetailPage />
                </ProtectedRoute>
              }
            />
            
            {/* Admin routes */}
            <Route
              path={ROUTES.ADMIN}
              element={
                <ProtectedRoute requireAdmin>
                  <AdminPage />
                </ProtectedRoute>
              }
            />
            
            {/* Redirect root to experiments */}
            <Route path="/" element={<Navigate to={ROUTES.EXPERIMENTS} replace />} />
            
            {/* 404 - redirect to experiments */}
            <Route path="*" element={<Navigate to={ROUTES.EXPERIMENTS} replace />} />
          </Routes>
        </NotificationProvider>
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
}

export default App;



