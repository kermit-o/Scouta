import React from 'react';
import IdeaAnalyzer from './components/IdeaAnalyzer';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>🚀 Forge SaaS</h1>
        <p>Transforma tus ideas en proyectos reales con IA</p>
        <div className="feature-tags">
          <span className="feature-tag">⚡ DeepSeek Integrado</span>
          <span className="feature-tag">🎯 Múltiples Generadores</span>
          <span className="feature-tag">🚀 Supera a lovable.dev</span>
        </div>
      </header>
      <main>
        <IdeaAnalyzer />
      </main>
      <footer>
        Forge SaaS - La plataforma definitiva para creación de proyectos con IA
      </footer>
    </div>
  );
}

export default App;
