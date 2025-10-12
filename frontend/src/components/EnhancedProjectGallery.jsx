import { useState } from 'react';
import './EnhancedProjectGallery.css';

const EnhancedProjectGallery = ({ projects }) => {
    const [selectedProject, setSelectedProject] = useState(null);

    return (
        <div className="enhanced-gallery">
            <div className="gallery-header">
                <h2>🚀 Tus Proyectos Forge SaaS</h2>
                <p>Gestiona y despliega todos tus proyectos en un solo lugar</p>
            </div>

            <div className="projects-stats">
                <div className="stat-card">
                    <h3>{projects.length}</h3>
                    <p>Proyectos Totales</p>
                </div>
                <div className="stat-card">
                    <h3>{projects.filter(p => p.deployment_status === 'deployed').length}</h3>
                    <p>Desplegados</p>
                </div>
                <div className="stat-card">
                    <h3>{projects.reduce((acc, p) => acc + (p.estimated_time || 0), 0)}</h3>
                    <p>Días Ahorrados</p>
                </div>
            </div>

            <div className="projects-grid">
                {projects.map(project => (
                    <ProjectCard 
                        key={project.id} 
                        project={project}
                        onSelect={setSelectedProject}
                    />
                ))}
            </div>

            {selectedProject && (
                <ProjectModal 
                    project={selectedProject}
                    onClose={() => setSelectedProject(null)}
                />
            )}
        </div>
    );
};
