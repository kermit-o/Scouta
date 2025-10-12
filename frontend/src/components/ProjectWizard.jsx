import React, { useState } from 'react'

const ProjectWizard = ({ onProjectCreate }) => {
  const [currentStep, setCurrentStep] = useState(1)
  const [projectData, setProjectData] = useState({
    name: '',
    description: '',
    projectType: 'react_web_app',
    features: [],
    technologies: [],
    authRequired: true,
    paymentIntegration: false,
    deploymentTarget: 'vercel'
  })

  const projectTypes = [
    { value: 'react_web_app', label: '🌐 React Web App', icon: '⚛️' },
    { value: 'nextjs_app', label: '▲ Next.js App', icon: '▲' },
    { value: 'vue_app', label: '�� Vue.js App', icon: '🟢' },
    { value: 'fastapi_service', label: '🐍 FastAPI Service', icon: '🐍' },
    { value: 'react_native_mobile', label: '📱 React Native', icon: '📱' },
    { value: 'chrome_extension', label: '🔧 Chrome Extension', icon: '🔧' },
    { value: 'ai_agent', label: '🤖 AI Agent', icon: '🤖' },
    { value: 'blockchain_dapp', label: '⛓️ Blockchain dApp', icon: '⛓️' }
  ]

  const features = [
    { id: 'auth', label: '🔐 Autenticación', description: 'Sistema de login y usuarios' },
    { id: 'payment', label: '💳 Pagos', description: 'Integración con Stripe/PayPal' },
    { id: 'admin_panel', label: '⚙️ Panel Admin', description: 'Dashboard de administración' },
    { id: 'real_time', label: '🔌 Tiempo Real', description: 'WebSockets y actualizaciones en vivo' },
    { id: 'ai_enhanced', label: '🧠 IA Integrada', description: 'Funcionalidades con inteligencia artificial' },
    { id: 'multi_tenant', label: '🏢 Multi-tenant', description: 'Soporte para múltiples clientes' }
  ]

  const technologies = [
    { id: 'react', label: 'React', color: 'bg-blue-100 text-blue-800' },
    { id: 'typescript', label: 'TypeScript', color: 'bg-blue-100 text-blue-800' },
    { id: 'tailwind', label: 'Tailwind CSS', color: 'bg-cyan-100 text-cyan-800' },
    { id: 'nodejs', label: 'Node.js', color: 'bg-green-100 text-green-800' },
    { id: 'python', label: 'Python', color: 'bg-yellow-100 text-yellow-800' },
    { id: 'postgresql', label: 'PostgreSQL', color: 'bg-blue-100 text-blue-800' },
    { id: 'mongodb', label: 'MongoDB', color: 'bg-green-100 text-green-800' }
  ]

  const handleFeatureToggle = (featureId) => {
    setProjectData(prev => ({
      ...prev,
      features: prev.features.includes(featureId)
        ? prev.features.filter(f => f !== featureId)
        : [...prev.features, featureId]
    }))
  }

  const handleTechnologyToggle = (techId) => {
    setProjectData(prev => ({
      ...prev,
      technologies: prev.technologies.includes(techId)
        ? prev.technologies.filter(t => t !== techId)
        : [...prev.technologies, techId]
    }))
  }

  const handleCreateProject = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/projects/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(projectData)
      })

      const result = await response.json()
      
      if (result.success) {
        onProjectCreate(result)
        setCurrentStep(5) // Success step
      } else {
        alert('Error creando proyecto: ' + result.error)
      }
    } catch (error) {
      alert('Error de conexión: ' + error.message)
    }
  }

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <h3 className="text-2xl font-bold text-gray-900">🎯 ¿Qué quieres crear?</h3>
            <p className="text-gray-600">Elige el tipo de proyecto que mejor se adapte a tus necesidades</p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {projectTypes.map(type => (
                <div
                  key={type.value}
                  className={`border-2 rounded-xl p-4 cursor-pointer transition-all duration-300 ${
                    projectData.projectType === type.value
                      ? 'border-blue-500 bg-blue-50 shadow-md'
                      : 'border-gray-200 hover:border-gray-300 hover:shadow-sm'
                  }`}
                  onClick={() => setProjectData(prev => ({ ...prev, projectType: type.value }))}
                >
                  <div className="text-2xl mb-2">{type.icon}</div>
                  <div className="font-semibold text-gray-900">{type.label}</div>
                </div>
              ))}
            </div>
          </div>
        )

      case 2:
        return (
          <div className="space-y-6">
            <h3 className="text-2xl font-bold text-gray-900">✨ Características</h3>
            <p className="text-gray-600">Selecciona las funcionalidades que necesitas</p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {features.map(feature => (
                <div
                  key={feature.id}
                  className={`border rounded-lg p-4 cursor-pointer transition-all duration-200 ${
                    projectData.features.includes(feature.id)
                      ? 'border-green-500 bg-green-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => handleFeatureToggle(feature.id)}
                >
                  <div className="flex items-center space-x-3">
                    <div className={`w-6 h-6 rounded border flex items-center justify-center ${
                      projectData.features.includes(feature.id)
                        ? 'bg-green-500 border-green-500 text-white'
                        : 'border-gray-300'
                    }`}>
                      {projectData.features.includes(feature.id) && '✓'}
                    </div>
                    <div>
                      <div className="font-semibold text-gray-900">{feature.label}</div>
                      <div className="text-sm text-gray-600">{feature.description}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )

      case 3:
        return (
          <div className="space-y-6">
            <h3 className="text-2xl font-bold text-gray-900">🛠️ Tecnologías</h3>
            <p className="text-gray-600">Elige tu stack tecnológico preferido</p>
            
            <div className="flex flex-wrap gap-3">
              {technologies.map(tech => (
                <button
                  key={tech.id}
                  className={`px-4 py-2 rounded-full font-medium transition-all duration-200 ${
                    projectData.technologies.includes(tech.id)
                      ? `${tech.color} border-2 border-current shadow-md`
                      : 'bg-gray-100 text-gray-700 border-2 border-transparent hover:bg-gray-200'
                  }`}
                  onClick={() => handleTechnologyToggle(tech.id)}
                >
                  {tech.label}
                </button>
              ))}
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  🏷️ Nombre del Proyecto
                </label>
                <input
                  type="text"
                  value={projectData.name}
                  onChange={(e) => setProjectData(prev => ({ ...prev, name: e.target.value }))}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Mi Startup App..."
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  📝 Descripción
                </label>
                <textarea
                  value={projectData.description}
                  onChange={(e) => setProjectData(prev => ({ ...prev, description: e.target.value }))}
                  rows="3"
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Describe tu proyecto..."
                />
              </div>
            </div>
          </div>
        )

      case 4:
        return (
          <div className="space-y-6">
            <h3 className="text-2xl font-bold text-gray-900">🎉 Resumen</h3>
            <p className="text-gray-600">Revisa tu proyecto antes de crearlo</p>
            
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">Detalles del Proyecto</h4>
                  <div className="space-y-2 text-sm">
                    <div><span className="font-medium">Nombre:</span> {projectData.name}</div>
                    <div><span className="font-medium">Tipo:</span> {projectTypes.find(t => t.value === projectData.projectType)?.label}</div>
                    <div><span className="font-medium">Descripción:</span> {projectData.description}</div>
                  </div>
                </div>
                
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">Características</h4>
                  <div className="flex flex-wrap gap-2">
                    {projectData.features.map(featureId => {
                      const feature = features.find(f => f.id === featureId)
                      return feature ? (
                        <span key={featureId} className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">
                          {feature.label}
                        </span>
                      ) : null
                    })}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )

      case 5:
        return (
          <div className="text-center space-y-6">
            <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto">
              <span className="text-3xl">🎉</span>
            </div>
            <h3 className="text-2xl font-bold text-gray-900">¡Proyecto Creado!</h3>
            <p className="text-gray-600">Tu proyecto ha sido generado exitosamente</p>
            <button
              onClick={() => setCurrentStep(1)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-xl font-semibold"
            >
              Crear Otro Proyecto
            </button>
          </div>
        )
    }
  }

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8">
      {/* Progress Steps */}
      <div className="flex justify-between mb-8 relative">
        {[1, 2, 3, 4].map(step => (
          <div key={step} className="flex flex-col items-center z-10">
            <div className={`w-12 h-12 rounded-full flex items-center justify-center font-semibold text-lg ${
              step === currentStep
                ? 'bg-blue-600 text-white'
                : step < currentStep
                ? 'bg-green-500 text-white'
                : 'bg-gray-200 text-gray-500'
            }`}>
              {step < currentStep ? '✓' : step}
            </div>
            <div className="text-sm mt-2 text-gray-600">Paso {step}</div>
          </div>
        ))}
        <div className="absolute top-6 left-12 right-12 h-1 bg-gray-200 -z-10">
          <div 
            className="h-full bg-green-500 transition-all duration-500"
            style={{ width: `${((currentStep - 1) / 3) * 100}%` }}
          ></div>
        </div>
      </div>

      {/* Step Content */}
      <div className="min-h-[400px]">
        {renderStep()}
      </div>

      {/* Navigation */}
      {currentStep < 5 && (
        <div className="flex justify-between pt-8 border-t border-gray-200">
          <button
            onClick={() => setCurrentStep(prev => Math.max(1, prev - 1))}
            disabled={currentStep === 1}
            className={`px-6 py-3 rounded-xl font-semibold ${
              currentStep === 1
                ? 'text-gray-400 cursor-not-allowed'
                : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            ← Anterior
          </button>
          
          <button
            onClick={() => {
              if (currentStep === 4) {
                handleCreateProject()
              } else {
                setCurrentStep(prev => Math.min(4, prev + 1))
              }
            }}
            className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-xl font-semibold transition-all duration-300 transform hover:scale-105"
          >
            {currentStep === 4 ? '🚀 Crear Proyecto' : 'Siguiente →'}
          </button>
        </div>
      )}
    </div>
  )
}

export default ProjectWizard
