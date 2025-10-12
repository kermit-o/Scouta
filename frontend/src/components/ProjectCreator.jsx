import { useState, useEffect } from 'react';
import { createProject, getProjectTypes, getTechnologies, checkApiHealth } from '../services/api';
import './ProjectCreator.css';

const ProjectCreator = ({ onProjectCreated }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    project_type: 'react_web_app',
    features: [],
    technologies: [],
    auth_required: true,
    payment_integration: false,
    deployment_target: 'vercel'
  });
  const [isCreating, setIsCreating] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const [projectTypes, setProjectTypes] = useState([]);
  const [technologies, setTechnologies] = useState({});
  const [apiStatus, setApiStatus] = useState('checking');
  const [error, setError] = useState(null);

  // Cargar datos iniciales
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setApiStatus('checking');
        
        // Verificar salud de la API
        const isHealthy = await checkApiHealth();
        if (!isHealthy) {
          setApiStatus('offline');
          console.warn('⚠️ API no disponible, usando datos locales');
        } else {
          setApiStatus('online');
        }

        // Cargar tipos de proyecto
        const typesData = await getProjectTypes();
        setProjectTypes(typesData.project_types || []);

        // Cargar tecnologías
        const techData = await getTechnologies();
        setTechnologies(techData.technologies || {});

      } catch (err) {
        setApiStatus('error');
        setError('Error cargando datos iniciales');
        console.error('Error loading initial data:', err);
      }
    };

    loadInitialData();
  }, []);

  const availableFeatures = [
    { id: 'auth', label: '🔐 Autenticación', description: 'Sistema de usuarios y login' },
    { id: 'payment', label: '💳 Sistema de Pagos', description: 'Integración con Stripe/PayPal' },
    { id: 'admin_panel', label: '⚙️ Panel Admin', description: 'Dashboard de administración' },
    { id: 'real_time', label: '🔌 Tiempo Real', description: 'WebSockets y updates en vivo' },
    { id: 'ai_enhanced', label: '🧠 IA Integrada', description: 'Funcionalidades con AI' },
    { id: 'multi_tenant', label: '🏢 Multi-tenant', description: 'Soporte múltiples clientes' }
  ];

  const handleFeatureToggle = (featureId) => {
    setFormData(prev => ({
      ...prev,
      features: prev.features.includes(featureId)
        ? prev.features.filter(f => f !== featureId)
        : [...prev.features, featureId]
    }));
  };

  const handleTechToggle = (techId) => {
    setFormData(prev => ({
      ...prev,
      technologies: prev.technologies.includes(techId)
        ? prev.technologies.filter(t => t !== techId)
        : [...prev.technologies, techId]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsCreating(true);
    setError(null);
    
    try {
      const result = await createProject(formData);
      if (result.success) {
        onProjectCreated(result);
        // Reset form
        setFormData({
          name: '',
          description: '',
          project_type: 'react_web_app',
          features: [],
          technologies: [],
          auth_required: true,
          payment_integration: false,
          deployment_target: 'vercel'
        });
        setCurrentStep(1);
      } else {
        setError(result.error || 'No se pudo crear el proyecto');
      }
    } catch (error) {
      setError('Error de conexión: ' + error.message);
    } finally {
      setIsCreating(false);
    }
  };

  const renderStep = () => {
    if (apiStatus === 'checking') {
      return (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Cargando...</p>
        </div>
      );
    }

    if (apiStatus === 'offline' || apiStatus === 'error') {
      return (
        <div className="offline-state">
          <div className="offline-icon">⚠️</div>
          <h3>Modo Sin Conexión</h3>
          <p>La API no está disponible, pero puedes previsualizar tu proyecto.</p>
          <button 
            className="retry-btn"
            onClick={() => window.location.reload()}
          >
            Reintentar Conexión
          </button>
        </div>
      );
    }

    switch (currentStep) {
      case 1:
        return (
          <div className="step-content">
            <h3>🎯 Tipo de Proyecto</h3>
            <p className="step-description">Elige qué tipo de aplicación quieres crear</p>
            
            <div className="project-types-grid">
              {(projectTypes.length > 0 ? projectTypes : [
                { value: 'react_web_app', label: '🌐 React Web App', description: 'Aplicación web moderna con React' },
                { value: 'nextjs_app', label: '▲ Next.js App', description: 'App con SSR y optimización SEO' },
                { value: 'vue_app', label: '🟢 Vue.js App', description: 'Aplicación Vue.js progresiva' },
                { value: 'fastapi_service', label: '🐍 FastAPI Service', description: 'API REST moderna con Python' }
              ]).map(type => (
                <div
                  key={type.value}
                  className={`project-type-card ${
                    formData.project_type === type.value ? 'selected' : ''
                  }`}
                  onClick={() => setFormData(prev => ({ ...prev, project_type: type.value }))}
                >
                  <div className="type-icon">{type.label.split(' ')[0]}</div>
                  <div className="type-info">
                    <div className="type-name">{type.label.split(' ').slice(1).join(' ')}</div>
                    <div className="type-description">{type.description}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );

      case 2:
        return (
          <div className="step-content">
            <h3>✨ Características</h3>
            <p className="step-description">Selecciona las funcionalidades que necesitas</p>
            
            <div className="features-grid">
              {availableFeatures.map(feature => (
                <div
                  key={feature.id}
                  className={`feature-card ${
                    formData.features.includes(feature.id) ? 'selected' : ''
                  }`}
                  onClick={() => handleFeatureToggle(feature.id)}
                >
                  <div className="feature-checkbox">
                    {formData.features.includes(feature.id) && '✓'}
                  </div>
                  <div className="feature-info">
                    <div className="feature-name">{feature.label}</div>
                    <div className="feature-description">{feature.description}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );

      case 3:
        return (
          <div className="step-content">
            <h3>🛠️ Tecnologías & Configuración</h3>
            <p className="step-description">Personaliza tu stack tecnológico</p>
            
            <div className="tech-section">
              <h4>Tecnologías Preferidas</h4>
              <div className="tech-tags">
                {Object.values(technologies).flat().map(tech => (
                  <button
                    key={tech}
                    type="button"
                    className={`tech-tag ${
                      formData.technologies.includes(tech) ? 'selected' : ''
                    }`}
                    onClick={() => handleTechToggle(tech)}
                  >
                    {tech}
                  </button>
                ))}
              </div>
            </div>

            <div className="form-fields">
              <div className="form-group">
                <label>🏷️ Nombre del Proyecto</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="Mi Startup App..."
                  required
                />
              </div>
              
              <div className="form-group">
                <label>📝 Descripción</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Describe tu proyecto..."
                  rows="3"
                  required
                />
              </div>

              <div className="toggle-group">
                <label className="toggle-item">
                  <input
                    type="checkbox"
                    checked={formData.auth_required}
                    onChange={(e) => setFormData(prev => ({ ...prev, auth_required: e.target.checked }))}
                  />
                  <span className="toggle-label">🔐 Sistema de Autenticación</span>
                </label>
                
                <label className="toggle-item">
                  <input
                    type="checkbox"
                    checked={formData.payment_integration}
                    onChange={(e) => setFormData(prev => ({ ...prev, payment_integration: e.target.checked }))}
                  />
                  <span className="toggle-label">💳 Integración de Pagos</span>
                </label>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="project-creator">
      {/* Status Indicator */}
      {apiStatus !== 'online' && (
        <div className={`api-status ${apiStatus}`}>
          {apiStatus === 'checking' && '🔍 Conectando...'}
          {apiStatus === 'offline' && '⚠️ Modo sin conexión'}
          {apiStatus === 'error' && '❌ Error de conexión'}
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="error-message">
          {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        {/* Progress Bar */}
        <div className="progress-bar">
          {[1, 2, 3].map(step => (
            <div
              key={step}
              className={`progress-step ${step === currentStep ? 'active' : ''} ${
                step < currentStep ? 'completed' : ''
              }`}
            >
              <div className="step-number">{step < currentStep ? '✓' : step}</div>
              <div className="step-label">Paso {step}</div>
            </div>
          ))}
        </div>

        {/* Step Content */}
        {renderStep()}

        {/* Navigation */}
        {apiStatus !== 'checking' && (
          <div className="form-navigation">
            {currentStep > 1 && (
              <button
                type="button"
                className="nav-btn secondary"
                onClick={() => setCurrentStep(prev => prev - 1)}
              >
                ← Anterior
              </button>
            )}
            
            {currentStep < 3 ? (
              <button
                type="button"
                className="nav-btn primary"
                onClick={() => setCurrentStep(prev => prev + 1)}
                disabled={apiStatus === 'offline' && currentStep === 3}
              >
                Siguiente →
              </button>
            ) : (
              <button
                type="submit"
                className="nav-btn primary create-btn"
                disabled={isCreating || !formData.name || apiStatus === 'offline'}
              >
                {isCreating ? '🔄 Creando...' : '🚀 Crear Proyecto'}
                {apiStatus === 'offline' && ' (No disponible)'}
              </button>
            )}
          </div>
        )}
      </form>
    </div>
  );
};

export default ProjectCreator;
