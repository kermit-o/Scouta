// Layout principal
import React from 'react';

export const metadata = {
  title: 'Mi Proyecto - Forge SaaS',
  description: 'Proyecto generado automáticamente',
};

export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body>
        <nav style={{ padding: '1rem', borderBottom: '1px solid #eee' }}>
          <strong>Forge SaaS</strong> - Proyecto Generado
        </nav>
        <main>
          {children}
        </main>
      </body>
    </html>
  );
}
