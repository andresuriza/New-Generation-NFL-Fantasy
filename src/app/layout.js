import { Outlet } from 'react-router-dom'
import Navbar from '../components/navbar'
import { AuthProvider } from '../context/authContext'

export default function Layout() {
  return (
    <AuthProvider>
      <Navbar />
      <Outlet />
    </AuthProvider>
  )
}
