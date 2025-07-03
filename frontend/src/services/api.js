// frontend/src/services/api.js - FIXED WITH NO AUTH SESSION PERSISTENCE

class APIService {
  constructor() {
    this.baseURL = this.getBackendURL();
    // Don't load any stored tokens - always start fresh
    this.token = null;
    this.refreshToken = null;
    console.log('API Service initialized with baseURL:', this.baseURL);
    
    // Clear any existing auth data on initialization
    this.clearAuthTokens();
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
    // Store temporarily in sessionStorage instead of localStorage
    // This means auth won't persist across browser sessions
    sessionStorage.setItem('auth_token', accessToken);
    sessionStorage.setItem('refresh_token', refreshToken);
  }

  clearAuthTokens() {
    this.token = null;
    this.refreshToken = null;
    // Clear both localStorage and sessionStorage
    localStorage.removeItem('auth_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_data');
    localStorage.removeItem('currentAssessmentId');
    localStorage.removeItem('currentAssessmentDomain');
    sessionStorage.removeItem('auth_token');
    sessionStorage.removeItem('refresh_token');
    sessionStorage.removeItem('user_data');
  }

  async makeRequest(endpoint, options = {}) {
    const maxRetries = 3; // Reduced retries
    const timeoutMs = 30000; // Reduced timeout
    let lastError;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        console.log(`Attempt ${attempt}: ${this.baseURL}${endpoint}`);
        
        const headers = {
          'Content-Type': 'application/json',
          ...options.headers,
        };
        
        const response = await fetch(`${this.baseURL}${endpoint}`, {
          ...options,
          headers,
          signal: AbortSignal.timeout(timeoutMs),
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
          await new Promise(resolve => setTimeout(resolve, 1000));
        }
      }
    }

    throw new Error(`All ${maxRetries} attempts failed. Last error: ${lastError.message}`);
  }

  // SIMPLIFIED AUTH METHODS - Mock implementation
  async signup(email, password, fullName) {
    try {
      // Mock signup success - in real implementation, call your backend
      console.log('Mock signup for:', email);
      return {
        success: true,
        dev_mode: true,
        message: 'Account created successfully (dev mode)'
      };
    } catch (error) {
      console.error('Signup failed:', error);
      throw new Error('Failed to create account. Please try again.');
    }
  }

  async login(email, password) {
    try {
      // Mock login success - validate Chargebee email domain
      const isChargebeeEmail = email.toLowerCase().includes('@chargebee.com');
      
      if (!isChargebeeEmail) {
        throw new Error('Please use a valid @chargebee.com email address');
      }
      
      if (password.length < 1) {
        throw new Error('Password is required');
      }
      
      // Mock user data
      const mockUser = {
        email: email,
        name: email.split('@')[0].replace('.', ' ').split(' ').map(word => 
          word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' '),
        role: 'Risk Analyst'
      };
      
      // Store user data temporarily
      sessionStorage.setItem('user_data', JSON.stringify(mockUser));
      
      console.log('Mock login successful for:', email);
      
      return {
        success: true,
        user: mockUser,
        session: {
          access_token: 'mock-token',
          refresh_token: 'mock-refresh'
        }
      };
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  }

  async logout() {
    try {
      console.log('Logging out user');
      this.clearAuthTokens();
    } catch (error) {
      console.error('Logout error:', error);
    }
  }

  async getCurrentUser() {
    try {
      // Return user from sessionStorage if available
      const userData = sessionStorage.getItem('user_data');
      if (userData) {
        return JSON.parse(userData);
      }
      return null;
    } catch (error) {
      console.error('Failed to get current user:', error);
      return null;
    }
  }

  async verifyEmail(email) {
    try {
      // Simple validation - just check if it's a Chargebee email
      const isChargebeeEmail = email.toLowerCase().includes('@chargebee.com');
      return { exists: false }; // Always return false for signup flow
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
      const response = await this.makeRequest(`/assessment/${domain}`, {
        method: 'POST'
      });
      return response;
    } catch (error) {
      console.error('Failed to create assessment:', error);
      throw new Error('Unable to create assessment.');
    }
  }

  async createAssessmentWithProgress(domain, assessmentType = 'standard') {
    try {
      return await this.makeRequest(`/assessment/${domain}`, {
        method: 'POST'
      });
    } catch (error) {
      console.error('Failed to create assessment:', error);
      throw new Error('Unable to create assessment.');
    }
  }

  async getAssessmentProgress(assessmentId) {
    try {
      return await this.makeRequest(`/assessment/progress/${assessmentId}`);
    } catch (error) {
      console.error('Failed to get assessment progress:', error);
      throw new Error('Unable to get assessment progress.');
    }
  }

  async getAssessmentResult(assessmentId) {
    try {
      return await this.makeRequest(`/assessment/result/${assessmentId}`);
    } catch (error) {
      console.error('Failed to get assessment result:', error);
      throw new Error('Unable to get assessment result.');
    }
  }

  async pollAssessmentUntilComplete(assessmentId, onProgressUpdate = null, maxWaitTime = 900000) {
    const startTime = Date.now();
    const pollInterval = 4000;
    let lastError = null;
    
    while (Date.now() - startTime < maxWaitTime) {
      try {
        const progress = await this.getAssessmentProgress(assessmentId);
        if (onProgressUpdate) {
          onProgressUpdate(progress);
        }
        if (progress.status === 'completed') {
          const result = await this.getAssessmentResult(assessmentId);
          return result;
        } else if (progress.status === 'failed') {
          throw new Error(`Assessment failed: ${progress.error || 'Unknown error'}`);
        }
        await new Promise(resolve => setTimeout(resolve, pollInterval));
      } catch (error) {
        lastError = error;
        console.error('Polling error:', error);
        if (error.message && error.message.includes('timeout')) {
          await new Promise(resolve => setTimeout(resolve, pollInterval));
          continue;
        } else {
          throw error;
        }
      }
    }
    return { result: null, error: 'The backend is waking up or is slow to respond. Please wait a minute and try again.' };
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