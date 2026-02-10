export interface ProjectResponse {
  id: string;
  user_id: string;
  project_name: string;
  requirements: string;
  status: string;
  technology_stack: any;
  generated_plan: any;
  result: any;
  created_at: string;
  updated_at: string;
}

export interface CreateProjectRequest {
  user_id: string;
  project_name: string;
  requirements: string;
}

export interface GenerationResponse {
  success: boolean;
  files: any[];
  message: string;
}

export const projectApi = {
  async list(): Promise<ProjectResponse[]> {
    const response = await fetch('/api/projects');
    if (!response.ok) throw new Error('Failed to fetch projects');
    return response.json();
  },
  
  async create(data: CreateProjectRequest): Promise<ProjectResponse> {
    const response = await fetch('/api/projects', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to create project');
    return response.json();
  },

  async plan(projectId: string): Promise<{ job_id: string; project_id: string; started: boolean }> {
    const response = await fetch(`/api/projects/${projectId}/plan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });
    if (!response.ok) throw new Error('Failed to start planning');
    return response.json();
  },

  async generate(projectId: string): Promise<{ job_id: string; project_id: string; started: boolean }> {
    const response = await fetch(`/api/projects/${projectId}/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });
    if (!response.ok) throw new Error('Failed to start generation');
    return response.json();
  },

  async getProgress(jobId: string): Promise<any> {
    const response = await fetch(`/api/progress/${jobId}`);
    if (!response.ok) throw new Error('Failed to get progress');
    return response.json();
  },

  async download(projectId: string): Promise<Blob> {
    const response = await fetch(`/api/projects/${projectId}/download`);
    if (!response.ok) throw new Error('Failed to download');
    return response.blob();
  }
};

// Alias para compatibilidad
export const ProjectAPI = projectApi;
