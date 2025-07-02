// frontend/src/services/api.js - FIXED WITH CORRECT ENDPOINTS

class APIService {
  constructor() {
    this.baseURL = this.getBackendURL();
    this.token = localStorage.getItem('auth_token');
    this.refreshToken = localStorage.getItem('refresh_token');
    console.log('API Service initialized with baseURL:', this.baseURL);
  }

  getBackendURL() {
    const currentHostname = window.location.hostname;
    
    // Check if we're on Render frontend
    if (currentHostname.includes('onrender.com')) {
      // Your actual backend URL from the logs
      return 'https://chargebee-kyb-backend.onrender.com';
    }
    
    // Local development
    if (currentHostname === 'localhost' || currentHostname === '127.0.0.1') {
      return 'http://localhost:8000';
    }
    
    // Fallback to production
    return 'https://chargebee-kyb-backend.onrender.com';
  }

  setAuthTokens(accessToken, refreshToken) {
    this.token = accessToken;
    this.refreshToken = refreshToken;
    localStorage.setItem('auth_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
  }

  clearAuthTokens() {
    this.token = null;
    this.refreshToken = null;
    localStorage.removeItem('auth_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_data');
  }

  async makeRequest(endpoint, options = {}) {
    const maxRetries = 3;
    let lastError;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        console.log(`Attempt ${attempt}: ${this.baseURL}${endpoint}`);
        
        // Add auth token to headers if available
        const headers = {
          'Content-Type': 'application/json',
          ...options.headers,
        };
        
        if (this.token && !endpoint.includes('/auth/')) {
          headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        const response = await fetch(`${this.baseURL}${endpoint}`, {
          ...options,
          headers,
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

  // Authentication methods - FIXED ENDPOINTS
  async signup(email, password, fullName) {
    try {
      const response = await this.makeRequest('/auth/signup', {
        method: 'POST',
        body: JSON.stringify({
          email,
          password,
          full_name: fullName
        })
      });
      return response;
    } catch (error) {
      console.error('Signup failed:', error);
      throw new Error('Failed to create account. Please try again.');
    }
  }

  async login(email, password) {
    try {
      // FIXED: Changed from /auth/login to /auth/signin
      const response = await this.makeRequest('/auth/signin', {
        method: 'POST',
        body: JSON.stringify({ email, password })
      });
      
      if (response.success && response.session) {
        // Store tokens
        this.setAuthTokens(response.session.access_token, response.session.refresh_token);
        
        // Store user data
        localStorage.setItem('user_data', JSON.stringify(response.user));
      }
      
      return response;
    } catch (error) {
      console.error('Login failed:', error);
      throw new Error('Invalid email or password');
    }
  }

  async logout() {
    try {
      // FIXED: Changed from /auth/logout to /auth/signout
      await this.makeRequest('/auth/signout', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.token}`
        }
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      this.clearAuthTokens();
    }
  }

  async getCurrentUser() {
    try {
      // FIXED: Changed from /auth/me to /auth/user
      const response = await this.makeRequest('/auth/user', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.token}`
        }
      });
      return response.user;
    } catch (error) {
      console.error('Failed to get current user:', error);
      return null;
    }
  }

  async verifyEmail(email) {
    try {
      // This endpoint doesn't exist in backend - let's skip it
      console.log('Email verification check skipped');
      return { exists: false };
    } catch (error) {
      console.error('Email verification failed:', error);
      return { exists: false };
    }
  }

  // Assessment methods remain the same
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
      return await this.makeRequest(`/assessment/${domain}`, {
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

  async generatePDFReport(assessmentId) {
    try {
      return await this.makeRequest(`/assessments/${assessmentId}/pdf`);
    } catch (error) {
      console.error('Failed to generate PDF:', error);
      throw new Error('Unable to generate PDF report.');
    }
  }
}

const apiService = new APIService();
export default apiService;
export { apiService };