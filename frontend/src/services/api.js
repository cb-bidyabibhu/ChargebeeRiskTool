// frontend/src/services/api.js - FIXED: Non-blocking API with proper polling
// COMPLETE FILE - Replace your entire api.js with this

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
    
    // Local development - use port 8001 since 8000 is occupied
    if (currentHostname === 'localhost' || currentHostname === '127.0.0.1') {
      return 'http://localhost:8001';
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
    const timeoutMs = 30000; // 30 second timeout for regular requests
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
          await new Promise(resolve => setTimeout(resolve, 1000));
        }
      }
    }

    throw lastError;
  }

  // FIXED: Authentication Methods
  async signup(email, password, fullName) {
    try {
      if (!this.validateChargebeeEmail(email)) {
        throw new Error('Please use a valid @chargebee.com email address');
      }

      const existsCheck = await this.checkUserExists(email);
      if (existsCheck.exists) {
        throw new Error('An account with this email already exists. Please login instead.');
      }

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
          message: response.message,
          user: response.user,
          requires_verification: response.requires_verification || false,
          dev_mode: response.dev_mode || false
        };
      } else {
        throw new Error(response.message || 'Failed to create account');
      }
    } catch (error) {
      console.error('Signup failed:', error);
      
      // Handle specific error cases
      if (error.message.includes('already exists') || error.message.includes('already registered')) {
        throw new Error('An account with this email already exists. Please login instead.');
      }
      
      throw error;
    }
  }

  async login(email, password) {
    try {
      if (!this.validateChargebeeEmail(email)) {
        throw new Error('Please use a valid @chargebee.com email address');
      }

      if (!password || password.length < 1) {
        throw new Error('Password is required');
      }

      const response = await this.makeRequest('/auth/signin', {
        method: 'POST',
        body: JSON.stringify({
          email: email,
          password: password
        })
      });

      // Handle email verification requirement
      if (response.requires_verification) {
        return {
          success: false,
          message: response.message,
          requires_verification: true,
          email: response.email
        };
      }

      if (response.success) {
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
      
      // Handle specific error cases
      if (error.message.includes('No account found')) {
        throw new Error('No account found with this email. Please sign up first.');
      } else if (error.message.includes('Please verify your email')) {
        return {
          success: false,
          message: error.message,
          requires_verification: true
        };
      }
      
      throw error;
    }
  }

  async logout() {
    try {
      if (this.token && !this.token.startsWith('dev-token')) {
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

      if (this.token.startsWith('dev-token')) {
        return this.user;
      }

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

  async checkUserExists(email) {
    try {
      if (!this.validateChargebeeEmail(email)) {
        throw new Error('Please use a valid @chargebee.com email address');
      }

      const response = await this.makeRequest('/auth/check-user', {
        method: 'POST',
        body: JSON.stringify({
          email: email
        })
      });

      return {
        exists: response.exists,
        message: response.message
      };
    } catch (error) {
      console.error('User existence check failed:', error);
      // In case of error, assume user doesn't exist to allow signup
      return {
        exists: false,
        message: 'Unable to verify user existence'
      };
    }
  }

  async verifyEmail(email) {
    // Alias for checkUserExists for consistency
    return this.checkUserExists(email);
  }

  validateChargebeeEmail(email) {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@chargebee\.com$/;
    return emailRegex.test(email);
  }

  // FIXED: Non-blocking Assessment Methods

  async createAssessment(domain) {
    try {
      console.log(`🚀 Starting NON-BLOCKING assessment for: ${domain}`);
      
      const response = await this.makeRequest(`/assessment/${domain}`, {
        method: 'POST'
      });
      
      console.log(`✅ Assessment started successfully:`, response);
      return response;
    } catch (error) {
      console.error('Failed to create assessment:', error);
      throw new Error('Unable to create assessment. Please try again.');
    }
  }

  // FIXED: Lightweight progress checking (non-blocking)
  async getAssessmentProgress(assessmentId) {
    try {
      // Use lightweight fetch with very short timeout for progress checks
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
      
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
        // Don't throw error for progress checks, just return default
        console.warn(`Progress check failed with status ${response.status}`);
        return {
          status: 'processing',
          progress: 0,
          current_step: 'Checking progress...',
          completed: false
        };
      }

      const data = await response.json();
      // Don't log every progress update to avoid spam
      return data;
      
    } catch (error) {
      // Don't log every progress error to avoid spam
      if (error.name !== 'AbortError') {
        console.warn('Progress check failed (non-critical):', error.message);
      }
      return {
        status: 'processing',
        progress: 0,
        current_step: 'Assessment in progress...',
        completed: false
      };
    }
  }

  async getAssessmentResult(assessmentId) {
    try {
      console.log(`📥 Fetching result for assessment: ${assessmentId}`);
      
      const response = await this.makeRequest(`/assessment/result/${assessmentId}`);
      
      console.log(`✅ Assessment result retrieved:`, response);
      return response;
    } catch (error) {
      console.error('Failed to get assessment result:', error);
      throw new Error('Unable to get assessment result.');
    }
  }

  // FIXED: Non-blocking polling that doesn't interfere with other operations
  pollAssessmentUntilComplete(assessmentId, onProgressUpdate, maxWaitTime = 900000) {
    return new Promise((resolve, reject) => {
      console.log(`🔄 Starting NON-BLOCKING polling for: ${assessmentId}`);
      
      const startTime = Date.now();
      const pollInterval = 5000; // 5 second intervals (less frequent to avoid spam)
      let pollCount = 0;
      let consecutiveErrors = 0;
      const maxErrors = 5;
      
      const poll = async () => {
        try {
          pollCount++;
          
          // Check timeout
          if (Date.now() - startTime > maxWaitTime) {
            console.error(`⏰ Assessment ${assessmentId} timed out after ${maxWaitTime/1000} seconds`);
            reject(new Error('Assessment timed out after 15 minutes'));
            return;
          }
          
          // Get progress (non-blocking)
          const progress = await this.getAssessmentProgress(assessmentId);
          
          // Reset error counter on successful response
          consecutiveErrors = 0;
          
          // Update UI
          if (onProgressUpdate) {
            onProgressUpdate(progress);
          }
          
          console.log(`📊 Poll ${pollCount}: ${progress.status} - ${progress.progress}% - ${progress.current_step}`);
          
          if (progress.status === 'completed' && progress.completed) {
            console.log(`✅ Assessment ${assessmentId} completed, fetching result...`);
            try {
              const result = await this.getAssessmentResult(assessmentId);
              console.log(`🎉 Assessment ${assessmentId} fully completed`);
              resolve(result);
            } catch (resultError) {
              console.error(`❌ Failed to get result for ${assessmentId}:`, resultError);
              reject(new Error(`Assessment completed but failed to get result: ${resultError.message}`));
            }
          } else if (progress.status === 'failed') {
            console.error(`❌ Assessment ${assessmentId} failed:`, progress.error);
            reject(new Error(progress.error || 'Assessment failed'));
          } else {
            // Still processing - schedule next poll using setTimeout (non-blocking)
            setTimeout(poll, pollInterval);
          }
          
        } catch (error) {
          consecutiveErrors++;
          console.warn(`⚠️ Poll error ${consecutiveErrors}/${maxErrors} for ${assessmentId}:`, error.message);
          
          if (consecutiveErrors >= maxErrors) {
            console.error(`❌ Too many consecutive polling errors for ${assessmentId}`);
            reject(new Error(`Polling failed after ${maxErrors} consecutive errors: ${error.message}`));
          } else {
            // Retry with longer delay
            setTimeout(poll, pollInterval * 2);
          }
        }
      };
      
      // Start first poll immediately
      poll();
    });
  }

  // All other API methods remain the same
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