// frontend/src/services/api.js
// COMPLETE FILE - Copy this entire content to: frontend/src/services/api.js

const API_BASE_URL = 'http://localhost:8000';

export const apiService = {
  // --- HEALTH AND STATUS ---
  
  async checkHealth() {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Health check failed:', error);
      throw new Error('Backend connection failed');
    }
  },

  async getApiInfo() {
    try {
      const response = await fetch(`${API_BASE_URL}/`);
      return await response.json();
    } catch (error) {
      console.error('API info failed:', error);
      throw new Error('Failed to get API information');
    }
  },

  // --- ASSESSMENT OPERATIONS ---
  
  async startAssessment(domain) {
    try {
      const response = await fetch(`${API_BASE_URL}/assessment/${encodeURIComponent(domain)}`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Assessment failed: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Assessment failed:', error);
      throw new Error(error.message || 'Assessment failed');
    }
  },

  async startEnhancedAssessment(domain) {
    try {
      const response = await fetch(`${API_BASE_URL}/enhanced-assessment/${encodeURIComponent(domain)}`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Enhanced assessment failed: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Enhanced assessment failed:', error);
      throw new Error(error.message || 'Enhanced assessment failed');
    }
  },

  async createLegacyAssessment(companyName) {
    try {
      const response = await fetch(`${API_BASE_URL}/new-assessment/${encodeURIComponent(companyName)}`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Legacy assessment failed: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Legacy assessment failed:', error);
      throw new Error(error.message || 'Legacy assessment failed');
    }
  },

  // --- DATA RETRIEVAL ---
  
  async fetchDomainAssessment(domain) {
    try {
      const response = await fetch(`${API_BASE_URL}/fetch-assessment/${encodeURIComponent(domain)}`, {
        headers: { 'Accept': 'application/json' }
      });
      
      if (response.status === 404) {
        return null; // No assessment found
      }
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Failed to fetch assessment: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Fetch assessment failed:', error);
      throw new Error(error.message || 'Failed to fetch assessment');
    }
  },

  async getAllAssessments(limit = 50, offset = 0) {
    try {
      const url = new URL(`${API_BASE_URL}/assessments`);
      url.searchParams.append('limit', limit.toString());
      url.searchParams.append('offset', offset.toString());
      
      const response = await fetch(url, {
        headers: { 'Accept': 'application/json' }
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Failed to fetch assessments: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Get all assessments failed:', error);
      throw new Error(error.message || 'Failed to fetch assessments');
    }
  },

  async getAssessmentById(assessmentId) {
    try {
      const response = await fetch(`${API_BASE_URL}/assessments/${encodeURIComponent(assessmentId)}`, {
        headers: { 'Accept': 'application/json' }
      });
      
      if (response.status === 404) {
        return null; // Assessment not found
      }
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Failed to fetch assessment: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Get assessment by ID failed:', error);
      throw new Error(error.message || 'Failed to fetch assessment');
    }
  },

  async getCompanyAssessments(companyName) {
    try {
      const response = await fetch(`${API_BASE_URL}/company/${encodeURIComponent(companyName)}/assessments`, {
        headers: { 'Accept': 'application/json' }
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Failed to fetch company assessments: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Get company assessments failed:', error);
      throw new Error(error.message || 'Failed to fetch company assessments');
    }
  },

  // --- SEARCH OPERATIONS ---
  
  async searchAssessments(query, limit = 20) {
    try {
      const url = new URL(`${API_BASE_URL}/assessments/search`);
      url.searchParams.append('query', query);
      url.searchParams.append('limit', limit.toString());
      
      const response = await fetch(url, {
        headers: { 'Accept': 'application/json' }
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Search failed: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Search assessments failed:', error);
      throw new Error(error.message || 'Failed to search assessments');
    }
  },

  // --- DELETE OPERATIONS ---
  
  async deleteAssessment(assessmentId) {
    try {
      const response = await fetch(`${API_BASE_URL}/assessments/${encodeURIComponent(assessmentId)}`, {
        method: 'DELETE',
        headers: { 'Accept': 'application/json' }
      });
      
      if (response.status === 404) {
        throw new Error('Assessment not found');
      }
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Delete failed: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Delete assessment failed:', error);
      throw new Error(error.message || 'Failed to delete assessment');
    }
  },

  async bulkDeleteAssessments(assessmentIds) {
    try {
      if (!Array.isArray(assessmentIds) || assessmentIds.length === 0) {
        throw new Error('No assessment IDs provided');
      }
      
      const response = await fetch(`${API_BASE_URL}/assessments/bulk-delete`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ assessment_ids: assessmentIds })
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Bulk delete failed: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Bulk delete failed:', error);
      throw new Error(error.message || 'Failed to bulk delete assessments');
    }
  },

  // --- UPDATE OPERATIONS ---
  
  async updateAssessment(assessmentId, updates) {
    try {
      const response = await fetch(`${API_BASE_URL}/assessments/${encodeURIComponent(assessmentId)}`, {
        method: 'PUT',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(updates)
      });
      
      if (response.status === 404) {
        throw new Error('Assessment not found');
      }
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Update failed: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Update assessment failed:', error);
      throw new Error(error.message || 'Failed to update assessment');
    }
  },

  // --- EXPORT OPERATIONS ---
  
  async exportAssessmentsCSV(format = 'detailed', limit = 1000) {
    try {
      const url = new URL(`${API_BASE_URL}/assessments/export/csv`);
      url.searchParams.append('format_type', format);
      url.searchParams.append('limit', limit.toString());
      
      const response = await fetch(url);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `CSV export failed: ${response.status}`);
      }

      // Get the blob and create download
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      
      // Extract filename from Content-Disposition header or create default
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = `risk_assessments_${new Date().toISOString().split('T')[0]}.csv`;
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]/g, '');
        }
      }
      
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(downloadUrl);
      
      return { 
        success: true, 
        message: 'CSV export completed',
        filename: filename,
        format: format 
      };
    } catch (error) {
      console.error('CSV export failed:', error);
      throw new Error(error.message || 'Failed to export CSV');
    }
  },

  async generatePDFReport(assessmentId) {
    try {
      const response = await fetch(`${API_BASE_URL}/assessments/${encodeURIComponent(assessmentId)}/pdf`, {
        headers: { 'Accept': 'application/json' }
      });
      
      if (response.status === 404) {
        throw new Error('Assessment not found');
      }
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `PDF generation failed: ${response.status}`);
      }
      
      const result = await response.json();
      
      if (result.success) {
        // For now, show the PDF template data
        console.log('PDF Template Data:', result.pdf_template_data);
        alert(`PDF Report Ready!\n\nCompany: ${result.company_name}\nNote: ${result.note}\n\nTemplate data logged to console.`);
        return result;
      } else {
        throw new Error('PDF generation failed');
      }
    } catch (error) {
      console.error('PDF generation failed:', error);
      throw new Error(error.message || 'Failed to generate PDF');
    }
  },

  // --- ANALYTICS AND STATISTICS ---
  
  async getRiskDistribution() {
    try {
      const response = await fetch(`${API_BASE_URL}/stats/risk-distribution`, {
        headers: { 'Accept': 'application/json' }
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Failed to get statistics: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Get risk distribution failed:', error);
      throw new Error(error.message || 'Failed to get statistics');
    }
  },

  async getAnalyticsSummary(days = 30) {
    try {
      const response = await fetch(`${API_BASE_URL}/analytics/summary?days=${days}`, {
        headers: { 'Accept': 'application/json' }
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Failed to get analytics: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Get analytics summary failed:', error);
      throw new Error(error.message || 'Failed to get analytics summary');
    }
  },

  async getAssessmentTrends(days = 30) {
    try {
      const response = await fetch(`${API_BASE_URL}/analytics/trends?days=${days}`, {
        headers: { 'Accept': 'application/json' }
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Failed to get trends: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Get trends failed:', error);
      throw new Error(error.message || 'Failed to get trends');
    }
  },

  // --- UTILITY FUNCTIONS ---
  
  async validateDomain(domain) {
    try {
      if (!domain || typeof domain !== 'string') {
        throw new Error('Domain is required');
      }
      
      const cleanDomain = domain
        .replace(/^https?:\/\//, '')
        .replace(/^www\./, '')
        .replace(/\/$/, '')
        .toLowerCase();
      
      if (!cleanDomain.includes('.') || cleanDomain.length < 3) {
        throw new Error('Invalid domain format');
      }
      
      return {
        isValid: true,
        cleanDomain: cleanDomain,
        originalDomain: domain
      };
    } catch (error) {
      return {
        isValid: false,
        error: error.message,
        originalDomain: domain
      };
    }
  },

  async testConnection() {
    try {
      const startTime = Date.now();
      const health = await this.checkHealth();
      const responseTime = Date.now() - startTime;
      
      return {
        isConnected: true,
        responseTime: responseTime,
        status: health.status,
        services: health.services,
        version: health.version
      };
    } catch (error) {
      return {
        isConnected: false,
        error: error.message,
        responseTime: null
      };
    }
  }
};

// Export utility functions
export const domainUtils = {
  formatDomainForDisplay: (domain) => {
    if (!domain) return '';
    return domain.replace(/^https?:\/\//, '').replace(/^www\./, '');
  },
  
  createDomainUrl: (domain, protocol = 'https') => {
    if (!domain) return '';
    const cleanDomain = domain.replace(/^https?:\/\//, '').replace(/^www\./, '');
    return `${protocol}://${cleanDomain}`;
  }
};

// Export risk assessment utilities
export const riskUtils = {
  getRiskColor: (score) => {
    if (score >= 7) return 'green';
    if (score >= 4) return 'yellow';
    return 'red';
  },
  
  getRiskLevel: (score) => {
    if (score >= 7) return 'Low';
    if (score >= 4) return 'Medium';
    return 'High';
  },
  
  formatScore: (score) => {
    if (typeof score !== 'number') return 'N/A';
    return score.toFixed(1);
  }
};

// Default export
export default apiService;