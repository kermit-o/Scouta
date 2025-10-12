import './ProjectGallery.css';

const ProjectGallery = ({ projects }) => {
  if (!projects || projects.length === 0) {
    return (
      <div className="project-gallery empty">
        <div className="empty-state">
          <div className="empty-icon">📁</div>
          <h3>No hay proyectos aún</h3>
          <p>Crea tu primer proyecto para verlo aquí</p>
        </div>
      </div>
    );
  }

  const getProjectTypeIcon = (type) => {
    const icons = {
      'react_web_app': '��',
      'nextjs_app': '▲',
      'vue_app': '🟢',
      'fastapi_service': '🐍',
      'react_native_mobile': '📱',
      'chrome_extension': '🔧',
      'ai_agent': '🤖',
      'blockchain_dapp': '⛓️'
    };
    return icons[type] || '📄';
  };

  const getFeatureBadges = (features) => {
    if (!features) return [];
    
    const featureIcons = {
      'auth': '🔐',
      'payment': '💳',
      'admin_panel': '⚙️',
      'real_time': '🔌',
      'ai_enhanced': '🧠',
      'multi_tenant': '��',
      'react_app': '⚛️',
      'vite_build': '⚡',
      'modern_ui': '🎨'
    };

    return features.slice(0, 4).map(feature => ({
      label: feature,
      icon: featureIcons[feature] || '✨'
    }));
  };

  return (
    <div className="project-gallery">
      <div className="gallery-header">
        <h2>📁 Proyectos Generados</h2>
        <p className="gallery-subtitle">
          {projects.length} proyecto{projects.length !== 1 ? 's' : ''} creado{projects.length !== 1 ? 's' : ''}
        </p>
      </div>

      <div className="projects-grid">
        {projects.map((project, index) => (
          <div key={project.project_id || index} className="project-card">
            <div className="project-header">
              <div className="project-type">
                <span className="type-icon">
                  {getProjectTypeIcon(project.project_type)}
                </span>
                <span className="type-label">
                  {project.project_type?.replace(/_/g, ' ') || 'react_web_app'}
                </span>
              </div>
              <div className="project-id">
                #{project.project_id || 'N/A'}
              </div>
            </div>

            <div className="project-content">
              <h3 className="project-name">{project.project_name}</h3>
              <p className="project-description">
                {project.requirements?.description || project.description || 'Sin descripción'}
              </p>

              {project.features_implemented && project.features_implemented.length > 0 && (
                <div className="project-features">
                  <div className="features-label">Características:</div>
                  <div className="features-badges">
                    {getFeatureBadges(project.features_implemented).map((feature, idx) => (
                      <span key={idx} className="feature-badge">
                        {feature.icon} {feature.label}
                      </span>
                    ))}
                    {project.features_implemented.length > 4 && (
                      <span className="feature-badge more">
                        +{project.features_implemented.length - 4} más
                      </span>
                    )}
                  </div>
                </div>
              )}
            </div>

            <div className="project-footer">
              <div className="project-actions">
                {project.project_path && (
                  <button 
                    className="action-btn primary"
                    onClick={() => {
                      // Navegar al directorio del proyecto
                      console.log('Abrir proyecto:', project.project_path);
                    }}
                  >
                    📂 Abrir Proyecto
                  </button>
                )}
                
                <button 
                  className="action-btn secondary"
                  onClick={() => {
                    // Mostrar detalles del proyecto
                    console.log('Detalles:', project);
                  }}
                >
                  ℹ️ Detalles
                </button>
              </div>

              {project.next_steps && project.next_steps.length > 0 && (
                <div className="next-steps">
                  <div className="steps-label">Próximos pasos:</div>
                  <div className="steps-list">
                    {project.next_steps.slice(0, 2).map((step, idx) => (
                      <div key={idx} className="step-item">
                        {step}
                      </div>
                    ))}
                    {project.next_steps.length > 2 && (
                      <div className="step-item more">
                        ...y {project.next_steps.length - 2} más
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {project.generated_at && (
              <div className="project-meta">
                <span className="timestamp">
                  Creado: {new Date(parseFloat(project.generated_at) * 1000).toLocaleDateString()}
                </span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProjectGallery;
