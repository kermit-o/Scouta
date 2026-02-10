// ui/app/(app)/billing/page.tsx

'use client';

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '@/components/Auth/AuthProvider';
import { useSearchParams } from 'next/navigation';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const creditPackages = [
    { key: "small", name: "Paquete Básico", credits: 100, price: 25.00, description: "Ideal para 10-15 generaciones de prueba." },
    { key: "medium", name: "Paquete Profesional", credits: 500, price: 100.00, description: "Para desarrollo continuo y proyectos medianos." },
    { key: "large", name: "Paquete Corporativo", credits: 1500, price: 250.00, description: "Máximo rendimiento y estabilidad." },
];

export default function BillingPage() {
    const { user, fetchUserCredits } = useAuth();
    const searchParams = useSearchParams();
    const [statusMessage, setStatusMessage] = useState<string | null>(null);
    const [isProcessing, setIsProcessing] = useState(false);

    // Manejo de la redirección de Stripe
    useEffect(() => {
        const success = searchParams.get('success');
        const canceled = searchParams.get('canceled');

        if (success) {
            setStatusMessage('✅ Pago completado con éxito. Actualizando saldo de créditos...');
            fetchUserCredits(); // Vuelve a cargar el saldo del usuario para actualizar la Navbar
        } else if (canceled) {
            setStatusMessage('❌ Pago cancelado. Puedes intentarlo de nuevo.');
        }
    }, [searchParams, fetchUserCredits]);

    const handlePurchase = async (packageKey: string) => {
        setIsProcessing(true);
        setStatusMessage(null);
        
        try {
            // Llamar al backend para crear la sesión de Stripe
            const response = await axios.post(`${API_URL}/api/billing/create-checkout-session`, { 
                package_key: packageKey 
            });

            // Redirigir al usuario a la URL de pago de Stripe
            window.location.href = response.data.url;

        } catch (err: any) {
            setStatusMessage(err.response?.data?.detail || 'Error al conectar con la pasarela de pago.');
            setIsProcessing(false);
        }
    };

    return (
        <div className="max-w-6xl mx-auto py-10">
            <h1 className="text-4xl font-extrabold text-gray-900 mb-2">Comprar Créditos para Generación</h1>
            <p className="text-xl text-gray-600 mb-8">1 crédito = 1/10 de la generación promedio de una aplicación.</p>

            <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-8 rounded-lg">
                <p className="text-lg font-medium text-blue-800">
                    💰 Tu Saldo Actual: **{user?.credits_balance ?? 0}** créditos.
                </p>
            </div>
            
            {statusMessage && (
                <div className={`p-4 mb-6 rounded-lg ${statusMessage.startsWith('✅') ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                    {statusMessage}
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {creditPackages.map((pkg) => (
                    <div key={pkg.key} className="bg-white p-6 rounded-xl shadow-lg border-t-4 border-blue-600 flex flex-col justify-between">
                        <div>
                            <h2 className="text-3xl font-bold mb-2 text-gray-900">{pkg.name}</h2>
                            <p className="text-5xl font-extrabold text-blue-600 mb-4">${pkg.price.toFixed(2)}</p>
                            <p className="text-gray-500 mb-4">{pkg.description}</p>
                            <ul className="space-y-2 text-gray-700 mb-6">
                                <li className="font-semibold">{pkg.credits} Créditos de Generación</li>
                                <li>Acceso Ilimitado a Agentes</li>
                            </ul>
                        </div>
                        <button
                            onClick={() => handlePurchase(pkg.key)}
                            disabled={isProcessing}
                            className="w-full py-3 rounded-lg text-white font-semibold transition duration-300 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400"
                        >
                            {isProcessing ? 'Redirigiendo a pago...' : 'Comprar Ahora'}
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
}