// frontend/src/services/api.js - FINAL FIX

class APIService {
  constructor() {
    this.baseURL = this.getBackendURL();
    console.log('API Service initialized with baseURL:', this.baseURL);
  }

  getBackendURL() {
    const currentHostname = window.location.hostname;
    
    // Check if we're on Render frontend
    if (currentHostname.includes('onrender.com')) {
      // REPLACE THIS URL WITH YOUR ACTUAL BACKEND URL FROM RENDER DASHBOARD
      return 'https://chargebee-kyb-backend.onrender.com';
    }
    
    // Local development
    if (currentHostname === 'localhost' || currentHostname === '127.0.0.1') {
      return 'http://localhost:8000';
    }
    
    // Fallback to production
    return 'https://chargebee-kyb-backend.onrender.com';
  }

  async makeRequest(endpoint, options = {}) {
    const maxRetries = 3;
    let lastError;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        console.log(`Attempt ${attempt}: ${this.baseURL}${endpoint}`);
        
        const response = await fetch(`${this.baseURL}${endpoint}`, {
          ...options,
          headers: {
            'Content-Type': 'application/json',
            ...options.headers,
          },
          signal: AbortSignal.timeout(30000),
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        return data;

      } catch (error) {
        console.error(`Attempt ${attempt} failed:`, error.message);
        lastError = error;
        
        if (attempt < maxRetries) {
          await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
        }
      }
    }

    throw new Error(`All ${maxRetries} attempts failed. Last error: ${lastError.message}`);
  }

  async checkBackendHealth() {
    try {
      const health = await this.makeRequest('/health');
      return health;
    } catch (error) {
      console.error('Backend health check failed:', error);
      throw error;
    }
  }

  async fetchAssessments() {
    try {
      return await this.makeRequest('/assessments');
    } catch (error) {
      console.error('Failed to fetch assessments:', error);
      throw new Error('Unable to load assessments.');
    }
  }

  async createAssessment(domain) {
    try {
      return await this.makeRequest(`/enhanced-assessment/${domain}`, {
        method: 'POST'
      });
    } catch (error) {
      console.error('Failed to create assessment:', error);
      throw new Error('Unable to create assessment.');
    }
  }

  async getAssessment(domain) {
    try {
      return await this.makeRequest(`/fetch-assessment/${domain}`);
    } catch (error) {
      console.error('Failed to get assessment:', error);
      throw new Error('Unable to fetch assessment data.');
    }
  }

  async getRiskDistribution() {
    try {
      return await this.makeRequest('/stats/risk-distribution');
    } catch (error) {
      console.error('Failed to get risk distribution:', error);
      throw new Error('Unable to load analytics data.');
    }
  }

  async deleteAssessment(id) {
    try {
      return await this.makeRequest(`/assessments/${id}`, {
        method: 'DELETE'
      });
    } catch (error) {
      console.error('Failed to delete assessment:', error);
      throw new Error('Unable to delete assessment.');
    }
  }

  async exportData(format = 'csv') {
    try {
      return await this.makeRequest(`/assessments/export/${format}`);
    } catch (error) {
      console.error('Failed to export data:', error);
      throw new Error('Unable to export data.');
    }
  }
}

const apiService = new APIService();
export default apiService;
export { apiService };