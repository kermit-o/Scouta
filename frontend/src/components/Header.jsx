import React from 'react'
import { Link, useLocation } from 'react-router-dom'

const Header = () => {
  const location = useLocation()

  return (
    <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">⚡</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Forge SaaS</h1>
              <p className="text-xs text-gray-500">Supera a lovable.dev</p>
            </div>
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <Link 
              to="/" 
              className={`font-medium transition-colors duration-200 ${
                location.pathname === '/' ? 'text-blue-600' : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              🎯 Crear
            </Link>
            <Link 
              to="/dashboard" 
              className={`font-medium transition-colors duration-200 ${
                location.pathname === '/dashboard' ? 'text-blue-600' : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              📊 Dashboard
            </Link>
            <Link 
              to="/marketplace" 
              className={`font-medium transition-colors duration-200 ${
                location.pathname === '/marketplace' ? 'text-blue-600' : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              🛍️ Marketplace
            </Link>
          </nav>

          {/* User Actions */}
          <div className="flex items-center space-x-4">
            <button className="hidden md:block text-gray-600 hover:text-gray-900 font-medium">
              🔍 Buscar
            </button>
            <button className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-2 rounded-xl font-medium hover:shadow-lg transition-all duration-300">
              Iniciar Sesión
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
