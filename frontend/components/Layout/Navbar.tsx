// ui/components/Layout/Navbar.tsx

'use client';

import Link from 'next/link';
import { useAuth } from '../Auth/AuthProvider';

export default function Navbar() {
    const { user, logout } = useAuth();

    return (
        <nav className="bg-white shadow-md sticky top-0 z-10">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">
                    {/* Logotipo y Navegación Principal */}
                    <div className="flex items-center">
                        <Link href="/dashboard" className="text-2xl font-bold text-blue-600">
                            Scouta Forge
                        </Link>
                        <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                            <Link href="/dashboard" className="text-gray-500 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition duration-150">
                                Proyectos
                            </Link>
                            <Link href="/create" className="text-gray-500 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition duration-150">
                                Nuevo Proyecto
                            </Link>
                        </div>
                    </div>

                    {/* Información del Usuario y Créditos (El elemento clave) */}
                    <div className="flex items-center space-x-4">
                        <div className="flex items-center bg-blue-50 border border-blue-200 text-blue-800 text-sm font-medium px-3 py-1 rounded-full">
                            ✨ Créditos: 
                            <span className="ml-2 font-bold">
                                {user?.credits_balance ?? 0}
                            </span>
                        </div>
                        
                        <Link href="/billing" className="text-sm font-medium text-blue-600 hover:text-blue-800">
                            Comprar
                        </Link>
                        
                        <span className="text-sm text-gray-700">|</span>

                        <div className="text-sm font-medium text-gray-700 hidden sm:block">
                            {user?.email}
                        </div>
                        
                        <button
                            onClick={logout}
                            className="text-sm text-red-600 hover:text-red-800 font-medium transition duration-150"
                        >
                            Salir
                        </button>
                    </div>
                </div>
            </div>
        </nav>
    );
}