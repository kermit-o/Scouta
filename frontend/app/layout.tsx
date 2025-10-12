// ui/app/layout.tsx

import './globals.css';
import { AuthProvider } from '../components/Auth/AuthProvider';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body>
        {/* Aquí integramos el AuthProvider */}
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}