// frontend/src/services/api.js - FIXED: Non-blocking API + Real Authentication

class APIService {
  constructor() {
    this.baseURL = this.getBackendURL();
    this.token = null;
    this.refreshToken = null;
    this.user = null;
    
    // Load stored auth data
    this.loadStoredAuth();
    
    console.log('API Service initialized with baseURL:', this.baseURL);
  }

  getBackendURL() {
    const currentHostname = window.location.hostname;
    
    // Check if we're on Render frontend
    if (currentHostname.includes('onrender.com')) {
      return 'https://chargebee-kyb-backend.onrender.com';
    }
    
    // Local development
    if (currentHostname === 'localhost' || currentHostname === '127.0.0.1') {
      return 'http://localhost:8000';
    }
    
    // Fallback to production
    return 'https://chargebee-kyb-backend.onrender.com';
  }

  loadStoredAuth() {
    try {
      this.token = localStorage.getItem('auth_token');
      this.refreshToken = localStorage.getItem('refresh_token');
      const userData = localStorage.getItem('user_data');
      if (userData) {
        this.user = JSON.parse(userData);
      }
    } catch (error) {
      console.error('Failed to load stored auth:', error);
      this.clearAuthTokens();
    }
  }

  setAuthTokens(accessToken, refreshToken, user) {
    this.token = accessToken;
    this.refreshToken = refreshToken;
    this.user = user;
    
    localStorage.setItem('auth_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
    localStorage.setItem('user_data', JSON.stringify(user));
  }

  clearAuthTokens() {
    this.token = null;
    this.refreshToken = null;
    this.user = null;
    
    localStorage.removeItem('auth_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_data');
    localStorage.removeItem('currentAssessmentId');
    localStorage.removeItem('currentAssessmentDomain');
    sessionStorage.clear();
  }

  // FIXED: Non-blocking makeRequest that won't interfere with other API calls
  async makeRequest(endpoint, options = {}) {
    const maxRetries = 2;
    const timeoutMs = 15000;
    let lastError;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
        
        const headers = {
          'Content-Type': 'application/json',
          ...options.headers,
        };
        
        // Only add auth header if we have a token
        if (this.token) {
          headers.Authorization = `Bearer ${this.token}`;
        }

        const response = await fetch(`${this.baseURL}${endpoint}`, {
          ...options,
          headers,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        // Handle authentication errors
        if (response.status === 401) {
          this.clearAuthTokens();
          throw new Error('Authentication required');
        }

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`HTTP ${response.status}: ${errorText || response.statusText}`);
        }

        const data = await response.json();
        return data;

      } catch (error) {
        console.error(`Request attempt ${attempt} failed:`, error.message);
        lastError = error;
        
        if (attempt < maxRetries && error.name !== 'AbortError') {
          await new Promise(resolve => setTimeout(resolve, 500));
        }
      }
    }

    throw lastError;
  }

  // FIXED: Proper Authentication Methods with Supabase Integration

  async signup(email, password, fullName) {
    try {
      // FIXED: Validate Chargebee email
      if (!this.validateChargebeeEmail(email)) {
        throw new Error('Please use a valid @chargebee.com email address');
      }

      // FIXED: Check if user already exists
      const existsCheck = await this.checkUserExists(email);
      if (existsCheck.exists) {
        throw new Error('An account with this email already exists. Please login instead.');
      }

      // Create user in Supabase Auth
      const response = await this.makeRequest('/auth/signup', {
        method: 'POST',
        body: JSON.stringify({
          email: email,
          password: password,
          full_name: fullName
        })
      });

      if (response.success) {
        return {
          success: true,
          message: response.dev_mode ? 
            'Account created successfully! You can now login.' :
            'Account created successfully! Please check your email to verify your account.',
          user: response.user,
          dev_mode: response.dev_mode
        };
      } else {
        throw new Error(response.message || 'Failed to create account');
      }
    } catch (error) {
      console.error('Signup failed:', error);
      throw error;
    }
  }

  async login(email, password) {
    try {
      // FIXED: Validate Chargebee email
      if (!this.validateChargebeeEmail(email)) {
        throw new Error('Please use a valid @chargebee.com email address');
      }

      if (!password || password.length < 1) {
        throw new Error('Password is required');
      }

      // FIXED: Authenticate with backend
      const response = await this.makeRequest('/auth/signin', {
        method: 'POST',
        body: JSON.stringify({
          email: email,
          password: password
        })
      });

      if (response.success) {
        // Store authentication data
        this.setAuthTokens(
          response.session.access_token,
          response.session.refresh_token,
          response.user
        );

        return {
          success: true,
          user: response.user,
          session: response.session
        };
      } else {
        throw new Error(response.message || 'Invalid email or password');
      }
    } catch (error) {
      console.error('Login failed:', error);
      throw new Error(error.message || 'Invalid email or password');
    }
  }

  async logout() {
    try {
      if (this.token && !this.token.startsWith('dev-token')) {
        // Call backend logout if we have a real token
        await this.makeRequest('/auth/signout', {
          method: 'POST'
        });
      }
    } catch (error) {
      console.error('Logout API call failed:', error);
    } finally {
      this.clearAuthTokens();
    }
  }

  async getCurrentUser() {
    try {
      if (!this.token) {
        return null;
      }

      // If it's a development token, return stored user
      if (this.token.startsWith('dev-token')) {
        return this.user;
      }

      // FIXED: Get current user from backend
      const response = await this.makeRequest('/auth/user');
      if (response.success) {
        return response.user;
      } else {
        this.clearAuthTokens();
        return null;
      }
    } catch (error) {
      console.error('Failed to get current user:', error);
      this.clearAuthTokens();
      return null;
    }
  }

  // FIXED: Check if user exists in system
  async checkUserExists(email) {
    try {
      // Don't require authentication for this check
      const response = await fetch(`${this.baseURL}/auth/check-user`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email })
      });

      if (response.ok) {
        const data = await response.json();
        return data;
      } else {
        // If endpoint doesn't exist, assume user doesn't exist
        return { exists: false };
      }
    } catch (error) {
      console.error('User check failed:', error);
      // If backend is unavailable, assume user doesn't exist
      return { exists: false };
    }
  }

  // FIXED: Proper email validation
  validateChargebeeEmail(email) {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@chargebee\.com$/;
    return emailRegex.test(email);
  }

  // FIXED: Non-blocking Assessment Methods

  async createAssessment(domain) {
    try {
      const response = await this.makeRequest(`/assessment/${domain}`, {
        method: 'POST'
      });
      return response;
    } catch (error) {
      console.error('Failed to create assessment:', error);
      throw new Error('Unable to create assessment. Please try again.');
    }
  }

  // FIXED: Non-blocking progress checking using separate lightweight requests
  async getAssessmentProgress(assessmentId) {
    try {
      // Use separate fetch with short timeout to avoid blocking other requests
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000); // Very short timeout for progress
      
      const response = await fetch(`${this.baseURL}/assessment/progress/${assessmentId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...(this.token && { Authorization: `Bearer ${this.token}` })
        },
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`Progress check failed: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      // Don't log every progress check error to avoid spam
      if (error.name !== 'AbortError') {
        console.warn('Progress check failed:', error.message);
      }
      throw error;
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

  // FIXED: Non-blocking polling using Web Workers concept (in-memory simulation)
  pollAssessmentUntilComplete(assessmentId, onProgressUpdate, maxWaitTime = 900000) {
    return new Promise((resolve, reject) => {
      const startTime = Date.now();
      const pollInterval = 4000; // 4 second intervals
      let pollCount = 0;
      const maxPolls = Math.ceil(maxWaitTime / pollInterval);
      
      const poll = async () => {
        try {
          pollCount++;
          
          // Check timeout
          if (Date.now() - startTime > maxWaitTime || pollCount > maxPolls) {
            reject(new Error('Assessment timed out after 15 minutes'));
            return;
          }
          
          // Use the lightweight progress check
          const progress = await this.getAssessmentProgress(assessmentId);
          
          if (onProgressUpdate) {
            onProgressUpdate(progress);
          }
          
          if (progress.status === 'completed') {
            const result = await this.getAssessmentResult(assessmentId);
            resolve(result);
          } else if (progress.status === 'failed') {
            reject(new Error(progress.error || 'Assessment failed'));
          } else {
            // Schedule next poll using requestIdleCallback to avoid blocking UI
            const scheduleNextPoll = () => {
              if (window.requestIdleCallback) {
                window.requestIdleCallback(() => {
                  setTimeout(poll, pollInterval);
                }, { timeout: pollInterval });
              } else {
                setTimeout(poll, pollInterval);
              }
            };
            
            scheduleNextPoll();
          }
          
        } catch (error) {
          // For network errors, retry a few times before giving up
          if (pollCount < 3) {
            setTimeout(poll, pollInterval);
          } else {
            reject(new Error(`Polling failed: ${error.message}`));
          }
        }
      };
      
      // Start polling immediately
      poll();
    });
  }

  // FIXED: All other API methods use the fixed makeRequest

  async checkBackendHealth() {
    try {
      return await this.makeRequest('/health');
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
      const response = await fetch(`${this.baseURL}/assessments/export/${format}`, {
        headers: {
          ...(this.token && { Authorization: `Bearer ${this.token}` })
        }
      });
      
      if (!response.ok) {
        throw new Error(`Export failed: ${response.status}`);
      }
      
      // Handle CSV download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `risk_assessments_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
      return { success: true, message: 'Export completed' };
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

  // Utility methods
  isAuthenticated() {
    return !!(this.token && this.user);
  }

  getUser() {
    return this.user;
  }
}

const apiService = new APIService();
export default apiService;
export { apiService };