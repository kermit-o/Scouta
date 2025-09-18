import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import { Button } from "./components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Textarea } from "./components/ui/textarea";
import { Progress } from "./components/ui/progress";
import { Badge } from "./components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Separator } from "./components/ui/separator";
import { ScrollArea } from "./components/ui/scroll-area";
import { 
  Loader2, 
  Lightbulb, 
  Code2, 
  FileText, 
  Download, 
  CheckCircle, 
  Clock,
  Zap,
  Sparkles,
  Rocket,
  Brain,
  Settings,
  FolderOpen
} from "lucide-react";
import { toast } from "sonner";
import { Toaster } from "./components/ui/sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Home = () => {
  const [idea, setIdea] = useState("");
  const [currentProject, setCurrentProject] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [projectDetails, setProjectDetails] = useState(null);
  const [recentProjects, setRecentProjects] = useState([]);

  useEffect(() => {
    fetchRecentProjects();
  }, []);

  const fetchRecentProjects = async () => {
    try {
      const response = await axios.get(`${API}/projects`);
      setRecentProjects(response.data.slice(0, 5));
    } catch (error) {
      console.error("Error fetching recent projects:", error);
    }
  };

  const handleSubmitIdea = async () => {
    if (!idea.trim()) {
      toast.error("Por favor, describe tu idea de aplicación");
      return;
    }

    setIsGenerating(true);
    setProgress(0);
    
    try {
      const response = await axios.post(`${API}/projects`, {
        user_description: idea
      });
      
      setCurrentProject(response.data);
      toast.success("¡Proyecto creado! Generando aplicación...");
      
      // Start polling for progress
      pollProgress(response.data.id);
      
    } catch (error) {
      console.error("Error creating project:", error);
      toast.error("Error al crear el proyecto");
      setIsGenerating(false);
    }
  };

  const pollProgress = async (projectId) => {
    const pollInterval = setInterval(async () => {
      try {
        const progressResponse = await axios.get(`${API}/projects/${projectId}/progress`);
        const progressData = progressResponse.data;
        
        setProgress(progressData.progress);
        
        if (progressData.progress >= 100 || progressData.status === 'completed') {
          clearInterval(pollInterval);
          setIsGenerating(false);
          fetchProjectDetails(projectId);
          toast.success("¡Aplicación generada exitosamente!");
          fetchRecentProjects(); // Refresh recent projects
        } else if (progressData.status === 'failed') {
          clearInterval(pollInterval);
          setIsGenerating(false);
          toast.error("Error en la generación del proyecto");
        }
      } catch (error) {
        console.error("Error polling progress:", error);
      }
    }, 2000);
  };

  const fetchProjectDetails = async (projectId) => {
    try {
      const [projectRes, funcSpecRes, techSpecRes, structureRes] = await Promise.allSettled([
        axios.get(`${API}/projects/${projectId}`),
        axios.get(`${API}/projects/${projectId}/functional-spec`),
        axios.get(`${API}/projects/${projectId}/tech-spec`),
        axios.get(`${API}/projects/${projectId}/structure`)
      ]);

      const details = {
        project: projectRes.status === 'fulfilled' ? projectRes.value.data : null,
        functionalSpec: funcSpecRes.status === 'fulfilled' ? funcSpecRes.value.data : null,
        techSpec: techSpecRes.status === 'fulfilled' ? techSpecRes.value.data : null,
        structure: structureRes.status === 'fulfilled' ? structureRes.value.data : null
      };

      setProjectDetails(details);
    } catch (error) {
      console.error("Error fetching project details:", error);
    }
  };

  const loadProject = async (projectId) => {
    setCurrentProject({ id: projectId });
    await fetchProjectDetails(projectId);
  };

  const resetProject = () => {
    setCurrentProject(null);
    setProjectDetails(null);
    setProgress(0);
    setIsGenerating(false);
    setIdea("");
  };

  if (currentProject && !isGenerating && projectDetails) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-emerald-100 rounded-lg">
                <CheckCircle className="h-6 w-6 text-emerald-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Aplicación Generada</h1>
                <p className="text-gray-600">Tu proyecto está listo</p>
              </div>
            </div>
            <Button onClick={resetProject} variant="outline">
              Nuevo Proyecto
            </Button>
          </div>

          <Tabs defaultValue="overview" className="space-y-6">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="overview">Resumen</TabsTrigger>
              <TabsTrigger value="functional">Funcional</TabsTrigger>
              <TabsTrigger value="technical">Técnico</TabsTrigger>
              <TabsTrigger value="structure">Estructura</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Lightbulb className="h-5 w-5 text-amber-500" />
                    Idea Original
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700 leading-relaxed">
                    {projectDetails.project?.user_description}
                  </p>
                </CardContent>
              </Card>

              {projectDetails.techSpec && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Settings className="h-5 w-5 text-blue-500" />
                      Stack Tecnológico Recomendado
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {projectDetails.techSpec.recommended_stack && Object.entries(projectDetails.techSpec.recommended_stack).map(([key, value]) => (
                        <div key={key} className="text-center">
                          <Badge variant="secondary" className="mb-2 capitalize">
                            {key}
                          </Badge>
                          <p className="text-sm font-medium">{value}</p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            <TabsContent value="functional" className="space-y-6">
              {projectDetails.functionalSpec && (
                <>
                  <Card>
                    <CardHeader>
                      <CardTitle>Historias de Usuario</CardTitle>
                      <CardDescription>Funcionalidades desde la perspectiva del usuario</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ScrollArea className="h-64">
                        <div className="space-y-3">
                          {projectDetails.functionalSpec.user_stories?.map((story, index) => (
                            <div key={index} className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                              <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center text-sm font-medium text-blue-600 flex-shrink-0">
                                {index + 1}
                              </div>
                              <p className="text-sm text-gray-700">{story}</p>
                            </div>
                          ))}
                        </div>
                      </ScrollArea>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle>Criterios de Aceptación</CardTitle>
                      <CardDescription>Condiciones que debe cumplir la aplicación</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ScrollArea className="h-48">
                        <div className="space-y-2">
                          {projectDetails.functionalSpec.acceptance_criteria?.map((criteria, index) => (
                            <div key={index} className="flex items-center gap-2">
                              <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                              <p className="text-sm text-gray-700">{criteria}</p>
                            </div>
                          ))}
                        </div>
                      </ScrollArea>
                    </CardContent>
                  </Card>
                </>
              )}
            </TabsContent>

            <TabsContent value="technical" className="space-y-6">
              {projectDetails.techSpec && (
                <>
                  <Card>
                    <CardHeader>
                      <CardTitle>Arquitectura</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-gray-700">{projectDetails.techSpec.architecture}</p>
                    </CardContent>
                  </Card>

                  {projectDetails.techSpec.endpoints?.length > 0 && (
                    <Card>
                      <CardHeader>
                        <CardTitle>API Endpoints</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <ScrollArea className="h-64">
                          <div className="space-y-3">
                            {projectDetails.techSpec.endpoints.map((endpoint, index) => (
                              <div key={index} className="border rounded-lg p-3">
                                <div className="flex items-center gap-2 mb-2">
                                  <Badge variant={endpoint.method === 'GET' ? 'default' : 'secondary'}>
                                    {endpoint.method}
                                  </Badge>
                                  <code className="text-sm bg-gray-100 px-2 py-1 rounded">
                                    {endpoint.path}
                                  </code>
                                </div>
                                <p className="text-sm text-gray-600">{endpoint.description}</p>
                              </div>
                            ))}
                          </div>
                        </ScrollArea>
                      </CardContent>
                    </Card>
                  )}

                  {projectDetails.techSpec.database_schema?.length > 0 && (
                    <Card>
                      <CardHeader>
                        <CardTitle>Esquema de Base de Datos</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          {projectDetails.techSpec.database_schema.map((schema, index) => (
                            <div key={index} className="border rounded-lg p-4">
                              <h4 className="font-medium mb-2">{schema.collection_name}</h4>
                              <div className="grid grid-cols-2 gap-2 text-sm">
                                {schema.fields && Object.entries(schema.fields).map(([field, type]) => (
                                  <div key={field} className="flex justify-between">
                                    <span className="font-mono">{field}</span>
                                    <span className="text-gray-500">{type}</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  )}
                </>
              )}
            </TabsContent>

            <TabsContent value="structure" className="space-y-6">
              {projectDetails.structure && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <FolderOpen className="h-5 w-5 text-orange-500" />
                      Estructura del Proyecto
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ScrollArea className="h-64">
                      <pre className="text-sm bg-gray-50 p-4 rounded-lg overflow-x-auto">
                        {JSON.stringify(projectDetails.structure.directory_tree, null, 2)}
                      </pre>
                    </ScrollArea>
                  </CardContent>
                </Card>
              )}
            </TabsContent>
          </Tabs>

          <div className="mt-8 flex gap-4">
            <Button size="lg" className="flex items-center gap-2">
              <Download className="h-4 w-4" />
              Descargar Proyecto
            </Button>
            <Button variant="outline" size="lg">
              Ver Código Generado
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50">
      <div className="container mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="flex items-center justify-center gap-3 mb-6">
            <div className="p-3 bg-gradient-to-r from-purple-500 to-blue-500 rounded-2xl">
              <Brain className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-5xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
              AppForge
            </h1>
          </div>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            Transforma cualquier idea en una aplicación web funcional. 
            Solo describe tu visión y nosotros generamos el código completo.
          </p>
        </div>

        {isGenerating ? (
          /* Generation Progress */
          <div className="max-w-2xl mx-auto">
            <Card className="border-2 border-blue-200 shadow-xl">
              <CardHeader className="text-center">
                <div className="flex items-center justify-center gap-2 mb-4">
                  <Loader2 className="h-6 w-6 animate-spin text-blue-500" />
                  <CardTitle className="text-2xl">Generando tu aplicación</CardTitle>
                </div>
                <CardDescription>
                  Estamos analizando tu idea y creando el código base...
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Progreso</span>
                    <span>{progress}%</span>
                  </div>
                  <Progress value={progress} className="h-3" />
                </div>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {[
                    { icon: Brain, label: "Análisis", threshold: 20 },
                    { icon: FileText, label: "Especificación", threshold: 40 },
                    { icon: Settings, label: "Arquitectura", threshold: 60 },
                    { icon: Code2, label: "Código", threshold: 80 }
                  ].map((stage, index) => (
                    <div key={index} className="text-center">
                      <div className={`p-3 rounded-full mx-auto mb-2 w-fit ${
                        progress >= stage.threshold 
                          ? 'bg-green-100 text-green-600' 
                          : progress >= stage.threshold - 20 
                            ? 'bg-blue-100 text-blue-600' 
                            : 'bg-gray-100 text-gray-400'
                      }`}>
                        <stage.icon className="h-5 w-5" />
                      </div>
                      <p className="text-sm font-medium">{stage.label}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        ) : (
          /* Idea Input Form */
          <div className="max-w-4xl mx-auto">
            <Card className="shadow-xl border-0 bg-white/70 backdrop-blur-sm">
              <CardHeader className="text-center">
                <CardTitle className="text-2xl flex items-center justify-center gap-2">
                  <Sparkles className="h-6 w-6 text-yellow-500" />
                  Describe tu idea
                </CardTitle>
                <CardDescription>
                  Explica tu aplicación con el mayor detalle posible. 
                  Incluye funcionalidades, usuarios objetivo y características especiales.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <Textarea
                  placeholder="Ejemplo: 'Quiero una aplicación para gestionar un hotel que permita a los huéspedes hacer check-in online, al personal coordinar limpieza y mantenimiento, y a los gerentes ver reportes en tiempo real. Necesita autenticación por roles, notificaciones push y integración con sistemas de pago...'"
                  value={idea}
                  onChange={(e) => setIdea(e.target.value)}
                  className="min-h-32 text-base"
                />
                
                <div className="flex flex-col sm:flex-row gap-3">
                  <Button 
                    onClick={handleSubmitIdea}
                    size="lg" 
                    className="flex-1 bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 text-white shadow-lg"
                  >
                    <Rocket className="h-4 w-4 mr-2" />
                    Generar Aplicación
                  </Button>
                  <Button variant="outline" size="lg" onClick={() => setIdea("")}>
                    Limpiar
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Recent Projects */}
            {recentProjects.length > 0 && (
              <Card className="mt-8 shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Clock className="h-5 w-5 text-gray-500" />
                    Proyectos Recientes
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {recentProjects.map((project) => (
                      <div 
                        key={project.id}
                        className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                        onClick={() => loadProject(project.id)}
                      >
                        <div className="flex-1">
                          <p className="font-medium truncate">
                            {project.user_description.substring(0, 60)}...
                          </p>
                          <p className="text-sm text-gray-500">
                            {new Date(project.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <Badge variant={project.status === 'completed' ? 'default' : 'secondary'}>
                          {project.status === 'completed' ? 'Completado' : 'En proceso'}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Features */}
            <div className="grid md:grid-cols-3 gap-6 mt-16">
              {[
                {
                  icon: Zap,
                  title: "Generación Rápida",
                  description: "De idea a código en minutos, no días",
                  color: "text-yellow-500"
                },
                {
                  icon: Brain,
                  title: "IA Avanzada",
                  description: "Análisis inteligente de requisitos y arquitectura",
                  color: "text-purple-500"
                },
                {
                  icon: Code2,
                  title: "Código Completo",
                  description: "Frontend, backend y base de datos listos para usar",
                  color: "text-blue-500"
                }
              ].map((feature, index) => (
                <Card key={index} className="text-center hover:shadow-lg transition-shadow">
                  <CardContent className="pt-6">
                    <div className={`p-3 rounded-full mx-auto mb-4 w-fit bg-gray-100 ${feature.color}`}>
                      <feature.icon className="h-6 w-6" />
                    </div>
                    <h3 className="font-semibold mb-2">{feature.title}</h3>
                    <p className="text-gray-600 text-sm">{feature.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}
      </div>
      <Toaster />
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;