import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import { AppLayout } from './components/common/AppLayout'
import { ToastContainer } from './components/common/Toast'
import { Login } from './pages/Login'
import { Register } from './pages/Register'
import { Dashboard } from './pages/Dashboard'
import { FoodRecognition } from './pages/FoodRecognition'
import { NutritionAnalysis } from './pages/NutritionAnalysis'
import { MealPlanner } from './pages/MealPlanner'
import { CheckIn } from './pages/CheckIn'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <>{children}</>
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/recognition" element={<FoodRecognition />} />
          <Route path="/nutrition" element={<NutritionAnalysis />} />
          <Route path="/meal-planner" element={<MealPlanner />} />
          <Route path="/checkin" element={<CheckIn />} />
        </Route>
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
      <ToastContainer />
    </BrowserRouter>
  )
}

export default App
