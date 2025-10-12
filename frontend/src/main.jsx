import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'

// Error Boundary para mejor manejo de errores
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error en la aplicación:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '20px', textAlign: 'center', fontFamily: 'Arial, sans-serif' }}>
          <h1>Algo salió mal</h1>
          <p>Recarga la página o verifica la consola para más detalles.</p>
          <button onClick={() => window.location.reload()}>
            Recargar Página
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// Render seguro
const rootElement = document.getElementById('root');
if (rootElement) {
  try {
    const root = ReactDOM.createRoot(rootElement);
    root.render(
      <React.StrictMode>
        <ErrorBoundary>
          <App />
        </ErrorBoundary>
      </React.StrictMode>,
    );
  } catch (error) {
    console.error('Error al renderizar la aplicación:', error);
    document.getElementById('root').innerHTML = `
      <div style="padding: 20px; text-align: center; font-family: Arial, sans-serif;">
        <h1>Error al cargar la aplicación</h1>
        <p>${error.message}</p>
        <button onclick="window.location.reload()">Recargar</button>
      </div>
    `;
  }
} else {
  console.error('Elemento root no encontrado');
}
