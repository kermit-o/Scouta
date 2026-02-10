// ui/app/(app)/layout.tsx

'use client';

import { useAuth } from '@/components/Auth/AuthProvider';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import Navbar from '@/components/Layout/Navbar'; // Componente que crearemos

export default function AppLayout({ children }: { children: React.ReactNode }) {
    const { isAuthenticated, loading } = useAuth();
    const router = useRouter();

    useEffect(() => {
        // Si no está cargando y NO está autenticado, redirigir a Login.
        if (!loading && !isAuthenticated) {
            router.push('/login');
        }
    }, [isAuthenticated, loading, router]);

    // Si está cargando o no autenticado, mostrar un spinner.
    if (loading || !isAuthenticated) {
        return (
            <div className="flex justify-center items-center h-screen bg-gray-50">
                <div className="text-blue-600 text-xl">Cargando aplicación...</div> 
                {/*  */}
            </div>
        );
    }

    // Si está autenticado, mostrar el Navbar y el contenido de la ruta.
    return (
        <div className="min-h-screen bg-gray-50">
            <Navbar />
            <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                {children}
            </main>
        </div>
    );
}