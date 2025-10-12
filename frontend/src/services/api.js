// API service for Forge SaaS
const API_BASE_URL = "http://localhost:8001/api/v1";

export const apiService = {
  // Payments
  async getPlans() {
    const response = await fetch(`${API_BASE_URL}/payments/plans`);
    return await response.json();
  },

  async createCheckoutSession(priceId) {
    const response = await fetch(`${API_BASE_URL}/payments/create-checkout-session`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ price_id: priceId })
    });
    return await response.json();
  },

  async getSubscription() {
    const response = await fetch(`${API_BASE_URL}/payments/subscription`);
    return await response.json();
  },

  // Projects
  async createProject(projectData) {
    const response = await fetch(`${API_BASE_URL}/projects`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(projectData)
    });
    return await response.json();
  },

  async getProjects() {
    const response = await fetch(`${API_BASE_URL}/projects`);
    return await response.json();
  },

  // AI Analysis
  async analyzeIdea(idea) {
    const response = await fetch(`${API_BASE_URL}/ai/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ idea })
    });
    return await response.json();
  }
};

export default apiService;
