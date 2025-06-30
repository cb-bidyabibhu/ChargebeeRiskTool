// frontend/src/services/api.js - Fixed API configuration

class APIService {
  constructor() {
    // Fix #1: Dynamic backend URL detection
    this.baseURL = this.getBackendURL();
    console.log('API Service initialized with baseURL:', this.baseURL);
  }

  getBackendURL() {
    // Check if we're in development or production
    const isDevelopment = window.location.hostname === 'localhost' || 
                         window.location.hostname === '127.0.0.1';
    
    if (isDevelopment) {
      // Try multiple local ports
      return 'http://localhost:8000';
    } else {
      // Production - use your Render backend URL
      return 'https://chargebee-kyb-backend.onrender.com';
    }
  }

  // Fix #2: Add retry logic and better error handling
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
          // Add timeout
          signal: AbortSignal.timeout(30000), // 30 second timeout
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

  // Fix #3: Health check method
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

  // Enhanced methods with better error handling
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
}

// Export singleton instance
const apiService = new APIService();
export default apiService;