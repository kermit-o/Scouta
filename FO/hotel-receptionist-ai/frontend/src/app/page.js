'use client'

import { useState, useEffect } from 'react'
import { 
  Phone, 
  Users, 
  Calendar, 
  BarChart3,
  Bell,
  Settings
} from 'lucide-react'

export default function Dashboard() {
  const [stats, setStats] = useState({
    activeCalls: 0,
    totalReservations: 0,
    todayCheckIns: 0,
    todayCheckOuts: 0
  })

  useEffect(() => {
    // Datos de prueba
    setStats({
      activeCalls: 3,
      totalReservations: 124,
      todayCheckIns: 8,
      todayCheckOuts: 5
    })
  }, [])

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800">🏨 Hotel Receptionist AI</h1>
        <p className="text-gray-600">Dashboard de administración</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Tarjeta de Llamadas Activas */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Llamadas Activas</p>
              <p className="text-3xl font-bold text-blue-600">{stats.activeCalls}</p>
            </div>
            <Phone className="w-10 h-10 text-blue-500" />
          </div>
        </div>

        {/* Tarjeta de Reservas Totales */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Reservas Totales</p>
              <p className="text-3xl font-bold text-green-600">{stats.totalReservations}</p>
            </div>
            <Calendar className="w-10 h-10 text-green-500" />
          </div>
        </div>

        {/* Tarjeta de Check-ins Hoy */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Check-ins Hoy</p>
              <p className="text-3xl font-bold text-purple-600">{stats.todayCheckIns}</p>
            </div>
            <Users className="w-10 h-10 text-purple-500" />
          </div>
        </div>

        {/* Tarjeta de Check-outs Hoy */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Check-outs Hoy</p>
              <p className="text-3xl font-bold text-orange-600">{stats.todayCheckOuts}</p>
            </div>
            <BarChart3 className="w-10 h-10 text-orange-500" />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sección de Llamadas Recientes */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-md p-6">
          <h2 className="text-xl font-bold mb-4">📞 Llamadas Recientes</h2>
          <div className="space-y-4">
            {[
              { number: '+34 123 456 789', time: '10:30', duration: '2:45', status: 'Resuelta' },
              { number: '+34 987 654 321', time: '11:15', duration: '1:30', status: 'En curso' },
              { number: '+34 555 123 456', time: '12:00', duration: '4:15', status: 'Resuelta' },
            ].map((call, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 border rounded-lg">
                <div>
                  <p className="font-medium">{call.number}</p>
                  <p className="text-sm text-gray-500">{call.time} • {call.duration}</p>
                </div>
                <span className={`px-3 py-1 rounded-full text-sm ${
                  call.status === 'Resuelta' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-blue-100 text-blue-800'
                }`}>
                  {call.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Sección de Acciones Rápidas */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <h2 className="text-xl font-bold mb-4">⚡ Acciones Rápidas</h2>
          <div className="space-y-3">
            <button className="w-full flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50">
              <span>Ver Todas las Llamadas</span>
              <Phone className="w-5 h-5" />
            </button>
            <button className="w-full flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50">
              <span>Gestionar Reservas</span>
              <Calendar className="w-5 h-5" />
            </button>
            <button className="w-full flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50">
              <span>Configurar IVR</span>
              <Settings className="w-5 h-5" />
            </button>
            <button className="w-full flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50">
              <span>Notificaciones</span>
              <Bell className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      <footer className="mt-8 text-center text-gray-500 text-sm">
        <p>Hotel Receptionist AI v1.0 • Sistema operativo</p>
      </footer>
    </div>
  )
}
