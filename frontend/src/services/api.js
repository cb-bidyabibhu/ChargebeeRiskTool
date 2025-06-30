// frontend/src/services/api.js - Fixed with proper export and environment detection

class APIService {
  constructor() {
    // Fix: Proper environment detection for Render deployment
    this.baseURL = this.getBackendURL();
    console.log('API Service initialized with baseURL:', this.baseURL);
    console.log('Current hostname:', window.location.hostname);
    console.log('Current href:', window.location.href);
  }

  getBackendURL() {
    const currentHostname = window.location.hostname;
    
    // Check if we're on Render (frontend deployed)
    if (currentHostname.includes('onrender.com')) {
      // Production - use your Render backend URL
      return 'https://chargebee-kyb-backend.onrender.com';
    }
    
    // Check if we're in local development
    if (currentHostname === 'localhost' || currentHostname === '127.0.0.1') {
      return 'http://localhost:8000';
    }
    
    // Default fallback to production
    return 'https://chargebee-kyb-backend.onrender.com';
  }

  // Add retry logic and better error handling
  async makeRequest(endpoint, options = {}) {
    const maxRetries = 3;
    let lastError;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        console.log(`Attempt ${attempt}: Making request to ${this.baseURL}${endpoint}`);
        
        const response = await fetch(`${this.baseURL}${endpoint}`, {
          ...options,
          headers: {
            'Content-Type': 'application/json',
            ...options.headers,
          },
          // Add timeout (30 seconds)
          signal: AbortSignal.timeout(30000),
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        console.log(`Request successful on attempt ${attempt}`);
        return data;

      } catch (error) {
        console.error(`Attempt ${attempt} failed:`, error.message);
        lastError = error;
        
        // If this is the last attempt, don't wait
        if (attempt < maxRetries) {
          // Wait before retrying (exponential backoff)
          await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
        }
      }
    }

    // All attempts failed
    throw new Error(`All ${maxRetries} attempts failed. Last error: ${lastError.message}`);
  }

  // Health check method
  async checkBackendHealth() {
    try {
      const health = await this.makeRequest('/health');
      console.log('Backend health check passed:', health);
      return health;
    } catch (error) {
      console.error('Backend health check failed:', error);
      throw error;
    }
  }

  // API Methods
  async fetchAssessments() {
    try {
      return await this.makeRequest('/assessments');
    } catch (error) {
      console.error('Failed to fetch assessments:', error);
      throw new Error('Unable to load assessments. Please check your connection.');
    }
  }

  async createAssessment(domain) {
    try {
      return await this.makeRequest(`/enhanced-assessment/${domain}`, {
        method: 'POST'
      });
    } catch (error) {
      console.error('Failed to create assessment:', error);
      throw new Error('Unable to create assessment. Please try again.');
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

// Create and export singleton instance
const apiService = new APIService();

// Fix: Proper export statements
export default apiService;
export { apiService };