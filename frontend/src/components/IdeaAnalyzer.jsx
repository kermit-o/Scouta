import React, { useState } from 'react';
import { analyzeIdea } from '../services/api';
import './IdeaAnalyzer.css';

const IdeaAnalyzer = () => {
  const [idea, setIdea] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAnalyze = async () => {
    if (!idea.trim()) {
      setError('Por favor ingresa una idea');
      return;
    }

    setLoading(true);
    setError('');
    setAnalysis(null);

    try {
      const result = await analyzeIdea(idea);
      setAnalysis(result);
    } catch (err) {
      setError('Error analizando la idea: ' + err.message);
      console.error('Error details:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateProject = () => {
    if (analysis) {
      alert(`🚀 Generando proyecto: ${analysis.project_type}\n\nEsta funcionalidad se conectará con el backend de generación.`);
      // TODO: Integrar con project generation API
    }
  };

  return (
    <div className="idea-analyzer">
      <h2>🚀 Analiza tu Idea con IA</h2>
      
      <div className="input-section">
        <textarea
          value={idea}
          onChange={(e) => setIdea(e.target.value)}
          placeholder="Describe tu idea de proyecto... Ejemplo: 'Quiero crear una app móvil para delivery de comida con chat en tiempo real'"
          rows="4"
        />
        <button 
          onClick={handleAnalyze} 
          disabled={loading || !idea.trim()}
        >
          {loading ? '🧠 Analizando...' : '🧠 Analizar Idea'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          ❌ {error}
        </div>
      )}

      {analysis && (
        <div className="analysis-result">
          <h3>✅ Análisis Completado</h3>
          
          <div className="analysis-grid">
            <div className="analysis-card">
              <h4>📊 Tipo de Proyecto</h4>
              <p>{analysis.project_type}</p>
            </div>
            
            <div className="analysis-card">
              <h4>🏗️ Arquitectura</h4>
              <p>{analysis.architecture}</p>
            </div>
            
            <div className="analysis-card">
              <h4>🛠️ Stack Recomendado</h4>
              <ul>
                {analysis.recommended_stack?.map((tech, index) => (
                  <li key={index}>{tech}</li>
                ))}
              </ul>
            </div>
            
            <div className="analysis-card">
              <h4>⚡ Complejidad</h4>
              <p>{analysis.complexity}</p>
            </div>
            
            <div className="analysis-card">
              <h4>📅 Tiempo Estimado</h4>
              <p>{analysis.estimated_weeks} semanas</p>
            </div>
            
            <div className="analysis-card">
              <h4>🚀 Deployment</h4>
              <p>{analysis.deployment_recommendation}</p>
            </div>
          </div>

          <div className="features-section">
            <h4>🎯 Características Principales</h4>
            <ul>
              {analysis.features?.map((feature, index) => (
                <li key={index}>{feature}</li>
              ))}
            </ul>
          </div>

          <div className="considerations-section">
            <h4>💡 Consideraciones Técnicas</h4>
            <ul>
              {analysis.technical_considerations?.map((consideration, index) => (
                <li key={index}>{consideration}</li>
              ))}
            </ul>
          </div>

          <button 
            onClick={handleGenerateProject}
            className="generate-button"
          >
            🚀 Generar Proyecto
          </button>
        </div>
      )}
    </div>
  );
};

export default IdeaAnalyzer;
