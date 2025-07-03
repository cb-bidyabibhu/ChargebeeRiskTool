import React, { useState, useEffect } from 'react';
import { 
  User, LogOut, FileText, BarChart3, Settings, Shield, TrendingUp, 
  Users, Database, Eye, PieChart, Calendar, Search, Plus, Filter, 
  Download, AlertTriangle, CheckCircle, XCircle, Clock, Activity,
  Globe, DollarSign, Lock, Building, Scale, RefreshCw, ExternalLink,
  Home, ChevronRight, Mail, Bell, ChevronDown, ChevronUp, Info,
  Zap, ShieldCheck, Trash2, FileDown, CheckSquare, Square,
  Edit3, Copy, Share2, UserPlus, ArrowLeft, X
} from 'lucide-react';

// Import the API service
import apiService from './services/api';
import ConnectionStatus from './components/ConnectionStatus';
import ExpandableDataView from './components/ExpandableDataView';

// Simple Toast Notification System
const ToastContext = React.createContext();

const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const addToast = (message, type = 'info', duration = 5000) => {
    const id = Date.now() + Math.random();
    const newToast = { id, message, type, duration };
    setToasts(prev => [...prev, newToast]);
    
    setTimeout(() => {
      removeToast(id);
    }, duration);
  };

  const removeToast = (id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };

  return (
    <ToastContext.Provider value={{ addToast, removeToast }}>
      {children}
      {/* Toast Container */}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {toasts.map(toast => (
          <div
            key={toast.id}
            className={`flex items-center justify-between p-4 rounded-lg shadow-lg max-w-sm transition-all duration-300 ${
              toast.type === 'success' ? 'bg-green-500 text-white' :
              toast.type === 'error' ? 'bg-red-500 text-white' :
              toast.type === 'warning' ? 'bg-yellow-500 text-white' :
              'bg-blue-500 text-white'
            }`}
          >
            <div className="flex items-center space-x-2">
              {toast.type === 'success' && <CheckCircle className="w-4 h-4" />}
              {toast.type === 'error' && <XCircle className="w-4 h-4" />}
              {toast.type === 'warning' && <AlertTriangle className="w-4 h-4" />}
              {toast.type === 'info' && <Info className="w-4 h-4" />}
              <span className="text-sm font-medium">{toast.message}</span>
            </div>
            <button
              onClick={() => removeToast(toast.id)}
              className="ml-2 text-white hover:text-gray-200"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
};

const useToast = () => {
  const context = React.useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

// Safe helper functions to prevent crashes
const safeGetCompanyName = (assessment) => {
  return assessment?.company_name || assessment?.domain || 'Unknown Company';
};

const safeGetDomain = (assessment) => {
  if (assessment?.domain) return assessment.domain;
  if (assessment?.company_name) {
    return `${assessment.company_name.toLowerCase().replace(/\s+/g, '')}.com`;
  }
  return 'unknown-domain.com';
};

const safeRenderAssessmentTitle = (assessment) => {
  const domain = assessment?.domain;
  const companyName = assessment?.company_name;
  
  if (domain) return domain;
  if (companyName) return `${companyName.toLowerCase()}.com`;
  return 'New Assessment';
};

const safeGetBusinessDomain = (assessment) => {
  if (assessment?.domain) return assessment.domain;
  if (assessment?.company_name) {
    return `${assessment.company_name.toLowerCase().replace(/\s+/g, '')}.com`;
  }
  return 'unknown-domain.com';
};

// Assessment Status Helper
const getAssessmentStatus = (assessment) => {
  if (assessment?.status) return assessment.status;
  if (assessment?.risk_assessment_data) return 'completed';
  return 'unknown';
};

const getStatusBadgeColor = (status) => {
  switch (status) {
    case 'processing': return 'bg-blue-100 text-blue-800';
    case 'completed': return 'bg-green-100 text-green-800';
    case 'failed': return 'bg-red-100 text-red-800';
    default: return 'bg-gray-100 text-gray-800';
  }
};

const getStatusIcon = (status) => {
  switch (status) {
    case 'processing': return <RefreshCw className="w-4 h-4 animate-spin" />;
    case 'completed': return <CheckCircle className="w-4 h-4" />;
    case 'failed': return <XCircle className="w-4 h-4" />;
    default: return <Clock className="w-4 h-4" />;
  }
};

// Copy to clipboard utility
const copyToClipboard = (text) => {
  navigator.clipboard.writeText(text).then(() => {
    // Toast will be shown by the calling component
  }).catch(err => {
    console.error('Failed to copy: ', err);
  });
};

// Mock user for demonstration
const mockUser = {
  email: 'bidya.bibhu@chargebee.com',
  name: 'Bidya Sharma',
  role: 'Risk Analyst'
};

// Enhanced Assessment State Management
const useAssessmentState = () => {
  const [inProgressAssessments, setInProgressAssessments] = useState(new Set());
  const [assessmentProgress, setAssessmentProgress] = useState({});
  
  const addInProgressAssessment = (assessmentId) => {
    setInProgressAssessments(prev => new Set([...prev, assessmentId]));
  };
  
  const removeInProgressAssessment = (assessmentId) => {
    setInProgressAssessments(prev => {
      const newSet = new Set(prev);
      newSet.delete(assessmentId);
      return newSet;
    });
  };
  
  const updateProgress = (assessmentId, progress) => {
    setAssessmentProgress(prev => ({
      ...prev,
      [assessmentId]: progress
    }));
  };
  
  return {
    inProgressAssessments,
    assessmentProgress,
    addInProgressAssessment,
    removeInProgressAssessment,
    updateProgress
  };
};

// Utility functions for export
const generatePDFReport = (assessment) => {
  if (assessment.id) {
    apiService.generatePDFReport(assessment.id)
      .then(result => {
        console.log('PDF generation result:', result);
        alert(`PDF report for ${safeGetCompanyName(assessment)} generated successfully!`);
      })
      .catch(error => {
        console.error('PDF generation failed:', error);
        alert(`Failed to generate PDF: ${error.message}`);
      });
  } else {
    alert(`PDF report for ${safeGetCompanyName(assessment)} would be generated here. Assessment ID required.`);
  }
};

const exportToCSV = (assessments) => {
  apiService.exportData('csv')
    .then(result => {
      console.log('CSV export completed:', result);
    })
    .catch(error => {
      console.error('CSV export failed:', error);
      // Fallback to client-side CSV generation
      const headers = ['Company Name', 'Domain', 'Risk Level', 'Score', 'Date', 'Assessment Type'];
      const csvData = assessments.map(assessment => [
        safeGetCompanyName(assessment),
        assessment.domain || 'N/A',
        assessment.risk_assessment_data?.risk_level || 'N/A',
        assessment.risk_assessment_data?.weighted_total_score?.toFixed(1) || 'N/A',
        new Date(assessment.created_at).toLocaleDateString(),
        'Assessment'
      ]);
      
      const csvContent = [headers, ...csvData]
        .map(row => row.map(field => `"${field}"`).join(','))
        .join('\n');
      
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `risk_assessments_${new Date().toISOString().split('T')[0]}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);
    });
};

// Login Component with Signup Flow
// Login Component with Supabase Authentication
const LoginPage = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSignup, setIsSignup] = useState(false);
  const [confirmPassword, setConfirmPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const validateChargebeeEmail = (email) => {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@chargebee\.com$/;
    return emailRegex.test(email);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    
    // Validate Chargebee email domain
    if (!validateChargebeeEmail(email)) {
      setError('Please use a valid @chargebee.com email address');
      return;
    }
    
    if (isSignup) {
      // Signup validation
      if (password.length < 6) {
        setError('Password must be at least 6 characters long');
        return;
      }
      
      if (password !== confirmPassword) {
        setError('Passwords do not match!');
        return;
      }
      
      if (name.trim().length < 2) {
        setError('Please enter your full name');
        return;
      }
      
      setIsLoading(true);
      
      try {
        // Call signup API
        const response = await apiService.signup(email, password, name);
        
        if (response.success) {
          if (response.dev_mode) {
            // In dev mode, auto-login after signup
            setSuccess('Account created! Logging you in...');
            setTimeout(async () => {
              setIsLoading(true);
              const loginResult = await onLogin(email, password);
              if (loginResult.success) {
                setIsSignup(false);
              } else {
                setError(loginResult.message);
              }
              setIsLoading(false);
            }, 1000);
          } else {
            setSuccess('Account created successfully! Please check your email to verify, then login.');
            setIsSignup(false);
          }
          setName('');
          setConfirmPassword('');
          setPassword('');
        } else {
          setError(response.message || 'Failed to create account');
        }
      } catch (error) {
        setError(error.message || 'Failed to create account');
      } finally {
        setIsLoading(false);
      }
      
    } else {
      // Login
      setIsLoading(true);
      const loginResult = await onLogin(email, password);
      if (loginResult.success) {
        // Login successful - component will unmount
      } else {
        setError(loginResult.message);
      }
      setIsLoading(false);
    }
  };

  // Check email availability on blur
  const handleEmailBlur = async () => {
    if (isSignup && validateChargebeeEmail(email)) {
      try {
        const response = await apiService.verifyEmail(email);
        if (response.exists) {
          setError('An account with this email already exists');
        }
      } catch (error) {
        // Ignore verification errors
      }
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md border border-gray-100">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-full mb-4 shadow-lg">
            <Shield className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">RiskBee KYB</h1>
          <p className="text-gray-600">
            {isSignup ? 'Create your account' : 'Risk Assessment Platform'}
          </p>
        </div>

        {/* Success message */}
        {success && (
          <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-sm text-green-600 flex items-center">
              <CheckCircle className="w-4 h-4 mr-2" />
              {success}
            </p>
          </div>
        )}

        {/* Error display */}
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-600 flex items-center">
              <AlertTriangle className="w-4 h-4 mr-2" />
              {error}
            </p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {isSignup && (
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Full Name
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Enter your full name"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                required
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              RiskBee Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
                setError(''); // Clear error when user types
              }}
              onBlur={handleEmailBlur}
              placeholder="your.name@riskbee.com"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              Must be a valid @riskbee.com email address
            </p>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                setError(''); // Clear error when user types
              }}
              placeholder="Enter your password"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              required
              minLength={isSignup ? 6 : 1}
            />
            {isSignup && (
              <p className="text-xs text-gray-500 mt-1">
                Minimum 6 characters
              </p>
            )}
          </div>

          {isSignup && (
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Confirm Password
              </label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => {
                  setConfirmPassword(e.target.value);
                  setError(''); // Clear error when user types
                }}
                placeholder="Confirm your password"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                required
              />
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-3 px-4 rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all font-semibold disabled:opacity-50 flex items-center justify-center"
          >
            {isLoading ? (
              <>
                <RefreshCw className="w-5 h-5 mr-2 animate-spin" />
                {isSignup ? 'Creating Account...' : 'Signing In...'}
              </>
            ) : (
              isSignup ? 'Create Account' : 'Sign In'
            )}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            {isSignup ? 'Already have an account?' : "Don't have an account?"}
            <button
              onClick={() => {
                setIsSignup(!isSignup);
                setPassword('');
                setConfirmPassword('');
                setError('');
                setSuccess('');
              }}
              className="ml-2 text-blue-600 hover:text-blue-700 font-semibold"
            >
              {isSignup ? 'Sign In' : 'Sign Up'}
            </button>
          </p>
        </div>

        {/* Forgot password link */}
        {!isSignup && (
          <div className="mt-4 text-center">
            <a href="#" className="text-sm text-blue-600 hover:text-blue-700">
              Forgot your password?
            </a>
          </div>
        )}
      </div>
    </div>
  );
};

// Header Component
const Header = ({ user, onLogout }) => {
  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4 sticky top-0 z-40">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">RiskBee KYB Platform</h1>
              <p className="text-xs text-gray-500">Risk Assessment System</p>
            </div>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <Mail className="w-4 h-4" />
            <span>{user.email}</span>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => window.open(apiService.baseURL + '/docs', '_blank')}
              className="flex items-center space-x-2 px-3 py-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all"
            >
              <FileText className="w-4 h-4" />
              <span className="hidden sm:inline">API Docs</span>
            </button>
            
            <button
              onClick={onLogout}
              className="flex items-center space-x-2 px-3 py-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all"
            >
              <LogOut className="w-4 h-4" />
              <span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

// Sidebar Component
const Sidebar = ({ currentPage, onPageChange }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Home },
    { id: 'assessments', label: 'Risk Assessments', icon: Shield },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'settings', label: 'Settings', icon: Settings }
  ];

  return (
    <aside className="w-64 bg-gray-50 border-r border-gray-200 h-full">
      <nav className="p-4 space-y-2">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => onPageChange(item.id)}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all text-left ${
              currentPage === item.id
                ? 'bg-blue-600 text-white shadow-lg'
                : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            <item.icon className="w-5 h-5" />
            <span className="font-medium">{item.label}</span>
            {currentPage === item.id && (
              <ChevronRight className="w-4 h-4 ml-auto" />
            )}
          </button>
        ))}
      </nav>
    </aside>
  );
};

// Chargebee-Style Dashboard Component
const ChargebeeStyleDashboard = () => {
  // State management
  const [domainInput, setDomainInput] = useState('');
  const [isAssessing, setIsAssessing] = useState(false);
  const [isFetching, setIsFetching] = useState(false);
  const [currentAssessment, setCurrentAssessment] = useState(null);
  const [recentAssessments, setRecentAssessments] = useState([]);
  const [expandedSections, setExpandedSections] = useState({});
  const [assessmentProgress, setAssessmentProgress] = useState(null);
  const [currentAssessmentId, setCurrentAssessmentId] = useState(null);
  const [showProcessingMessage, setShowProcessingMessage] = useState(false);
  const [assessmentPollingError, setAssessmentPollingError] = useState(null);
  
  // Enhanced state management
  const {
    inProgressAssessments,
    assessmentProgress: globalProgress,
    addInProgressAssessment,
    removeInProgressAssessment,
    updateProgress
  } = useAssessmentState();
  
  const { addToast } = useToast();

  // Load data on component mount
  useEffect(() => {
    loadRecentAssessments();
  }, []);
  
  // Auto-poll in-progress assessments
  useEffect(() => {
    if (inProgressAssessments.size === 0) return;
    
    const pollInterval = setInterval(async () => {
      for (const assessmentId of inProgressAssessments) {
        try {
          const progress = await apiService.getAssessmentProgress(assessmentId);
          updateProgress(assessmentId, progress);
          
          if (progress.status === 'completed') {
            const result = await apiService.getAssessmentResult(assessmentId);
            removeInProgressAssessment(assessmentId);
            addToast(`Assessment ${assessmentId} completed!`, 'success');
            loadRecentAssessments();
          } else if (progress.status === 'failed') {
            removeInProgressAssessment(assessmentId);
            addToast(`Assessment ${assessmentId} failed: ${progress.error || 'Unknown error'}`, 'error');
          }
        } catch (error) {
          console.error(`Failed to poll assessment ${assessmentId}:`, error);
        }
      }
    }, 10000); // Poll every 10 seconds
    
    return () => clearInterval(pollInterval);
  }, [inProgressAssessments]);

  // Load recent assessments
  const loadRecentAssessments = async () => {
    try {
      const assessments = await apiService.fetchAssessments();
      setRecentAssessments(assessments);
    } catch (error) {
      console.error('Failed to load assessments:', error);
      setRecentAssessments([]);
    }
  };

  // Poll function for assessment completion
  const pollAssessment = async (assessmentId, domainName) => {
    try {
      const result = await apiService.pollAssessmentUntilComplete(
        assessmentId,
        (progress) => {
          setAssessmentProgress(progress);
          updateProgress(assessmentId, progress);
        }
      );
      if (result && result.error) {
        setAssessmentPollingError(result.error);
        setAssessmentProgress(null);
        setShowProcessingMessage(false);
        removeInProgressAssessment(assessmentId);
        localStorage.removeItem('currentAssessmentId');
        localStorage.removeItem('currentAssessmentDomain');
        setIsAssessing(false);
        setCurrentAssessmentId(null);
        return;
      }
      setCurrentAssessment(result.result);
      setAssessmentProgress(null);
      setShowProcessingMessage(false);
      removeInProgressAssessment(assessmentId);
      addToast(`Assessment completed for ${domainName}`, 'success');
      localStorage.removeItem('currentAssessmentId');
      localStorage.removeItem('currentAssessmentDomain');
      setTimeout(loadRecentAssessments, 1000);
    } catch (error) {
      setAssessmentProgress(null);
      setShowProcessingMessage(false);
      removeInProgressAssessment(assessmentId);
      addToast(`Assessment failed for ${domainName}: ${error.message}`, 'error');
      localStorage.removeItem('currentAssessmentId');
      localStorage.removeItem('currentAssessmentDomain');
      setAssessmentPollingError(error.message);
      setIsAssessing(false);
      setCurrentAssessmentId(null);
    } finally {
      setIsAssessing(false);
      setCurrentAssessmentId(null);
    }
  };

  // FIXED: Handle NEW assessment with progress tracking
  const handleStartAssessment = async () => {
    if (!domainInput.trim()) return;
    setIsAssessing(true);
    setAssessmentProgress({ status: 'processing', progress: 0, current_step: 'Starting assessment...' });
    setCurrentAssessment(null);
    setShowProcessingMessage(false);
    setAssessmentPollingError(null);
    try {
      console.log(`🚀 Creating NEW assessment for: ${domainInput}`);
      // Start async assessment, get assessment_id
      const response = await apiService.createAssessment(domainInput);
      const assessmentId = response.assessment_id;
      setCurrentAssessmentId(assessmentId);
      addInProgressAssessment(assessmentId);
      addToast(`Assessment started for ${domainInput}`, 'info');
      setDomainInput('');
      setShowProcessingMessage(true);
      
      // Save to localStorage for persistence
      localStorage.setItem('currentAssessmentId', assessmentId);
      localStorage.setItem('currentAssessmentDomain', domainInput);
      
      // Start polling for progress
      pollAssessment(assessmentId, domainInput);
    } catch (error) {
      setIsAssessing(false);
      setAssessmentProgress(null);
      setCurrentAssessmentId(null);
      setShowProcessingMessage(false);
      addToast(`Failed to start assessment: ${error.message}`, 'error');
      alert(`New assessment failed: ${error.message}`);
    }
  };

  // New: Manual check status by assessment ID
  const handleCheckStatus = async () => {
    if (!currentAssessmentId) {
      addToast('No assessment in progress.', 'warning');
      return;
    }
    setIsAssessing(true);
    try {
      const progress = await apiService.getAssessmentProgress(currentAssessmentId);
      setAssessmentProgress(progress);
      updateProgress(currentAssessmentId, progress);
      
      if (progress.status === 'completed') {
        const result = await apiService.getAssessmentResult(currentAssessmentId);
        setCurrentAssessment(result.result);
        setAssessmentProgress(null);
        setCurrentAssessmentId(null);
        removeInProgressAssessment(currentAssessmentId);
        addToast('Assessment completed!', 'success');
        localStorage.removeItem('currentAssessmentId');
        localStorage.removeItem('currentAssessmentDomain');
        setTimeout(loadRecentAssessments, 1000);
      } else if (progress.status === 'failed') {
        addToast(`Assessment failed: ${progress.error || 'Unknown error'}`, 'error');
        setAssessmentProgress(null);
        setCurrentAssessmentId(null);
        removeInProgressAssessment(currentAssessmentId);
        localStorage.removeItem('currentAssessmentId');
        localStorage.removeItem('currentAssessmentDomain');
      }
    } catch (error) {
      addToast(`Failed to check assessment status: ${error.message}`, 'error');
    } finally {
      setIsAssessing(false);
    }
  };

  // FIXED: Handle FETCH existing assessment (Fetch existing from database)
  const handleFetchAssessment = async () => {
    if (!domainInput.trim()) return;
    
    setIsFetching(true);
    try {
      console.log(`🔍 Fetching existing assessment for: ${domainInput}`);
      const result = await apiService.getAssessment(domainInput);
      
      // Extract the data from the response
      if (result && result.data) {
        setCurrentAssessment(result.data);
        setDomainInput('');
      } else if (result) {
        setCurrentAssessment(result);
        setDomainInput('');
      } else {
        alert(`No existing assessment found for ${domainInput}. Try creating a new assessment instead.`);
      }
    } catch (error) {
      alert(`Failed to fetch existing assessment: ${error.message}`);
    } finally {
      setIsFetching(false);
    }
  };

  // Select assessment from recent list
  const selectAssessment = (assessment) => {
    setCurrentAssessment(assessment);
  };

  // Toggle section expansion
  const toggleSection = (sectionId) => {
    setExpandedSections(prev => ({
      ...prev,
      [sectionId]: !prev[sectionId]
    }));
  };

  // Get risk color based on score
  const getRiskColor = (score) => {
    if (score >= 7) return 'text-green-600';
    if (score >= 4) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getRiskBgColor = (score) => {
    if (score >= 7) return 'bg-green-50';
    if (score >= 4) return 'bg-yellow-50';
    return 'bg-red-50';
  };

  const getRiskBorderColor = (score) => {
    if (score >= 7) return 'border-green-200';
    if (score >= 4) return 'border-yellow-200';
    return 'border-red-200';
  };

  const getRiskLevel = (score) => {
    if (score >= 7) return 'LOW RISK';
    if (score >= 4) return 'MED RISK';
    return 'HIGH RISK';
  };

  const getRiskBadgeColor = (risk) => {
    switch (risk?.toLowerCase()) {
      case 'low': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'high': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatRiskCategory = (key) => {
    return key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
  };

  return (
    <div className="p-6">
      <div className="max-w-7xl mx-auto">
        {/* CONNECTION STATUS */}
        <div className="mb-6">
          <ConnectionStatus />
        </div>
        {/* Assessment Processing Status - Only show when actually processing */}
        {showProcessingMessage && currentAssessmentId && (
          <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-800 flex flex-col items-start">
            <div className="font-semibold mb-1">Assessment is processing...</div>
            <div className="text-xs mb-2 flex items-center space-x-2">
              <span>Assessment ID: <span className="font-mono">{currentAssessmentId}</span></span>
              <button
                onClick={() => {
                  copyToClipboard(currentAssessmentId);
                  addToast('Assessment ID copied to clipboard!', 'success');
                }}
                className="text-blue-600 hover:text-blue-800 p-1 rounded"
                title="Copy Assessment ID"
              >
                <Copy className="w-3 h-3" />
              </button>
            </div>
            <div className="text-xs mb-2">You can check the status later from the dashboard or by clicking below.</div>
            <div className="flex space-x-2">
              <button
                className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-xs"
                onClick={handleCheckStatus}
                disabled={isAssessing}
              >
                {isAssessing ? (
                  <>
                    <RefreshCw className="w-3 h-3 mr-1 animate-spin" />
                    Checking...
                  </>
                ) : (
                  'Check Status'
                )}
              </button>
              <button
                className="px-3 py-1 bg-gray-600 text-white rounded hover:bg-gray-700 text-xs"
                onClick={() => {
                  setShowProcessingMessage(false);
                  setCurrentAssessmentId(null);
                  localStorage.removeItem('currentAssessmentId');
                  localStorage.removeItem('currentAssessmentDomain');
                  addToast('Assessment tracking cleared', 'info');
                }}
                title="Clear this notification"
              >
                Dismiss
              </button>
            </div>
            <div className="text-xs mt-2 text-gray-500">Note: If the server was sleeping, this may take a few minutes to start. You can safely leave and check back later.</div>
          </div>
        )}

        {/* Risk Assessment Infographic - Show when no assessment is in progress */}
        {!showProcessingMessage && !currentAssessment && (
          <div className="mb-6 bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-6">
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <Shield className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Comprehensive Risk Assessment</h2>
              <p className="text-gray-600">Get detailed insights into business risk and compliance across 5 major categories</p>
            </div>
            
            {/* 5 Major Risk Categories */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
              <div className="bg-white rounded-lg p-4 border border-gray-200 text-center">
                <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <Shield className="w-5 h-5 text-red-600" />
                </div>
                <h3 className="font-semibold text-gray-900 text-sm mb-1">Security Risk</h3>
                <p className="text-xs text-gray-600">SSL certificates, malware detection, security headers</p>
              </div>
              
              <div className="bg-white rounded-lg p-4 border border-gray-200 text-center">
                <div className="w-10 h-10 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <Globe className="w-5 h-5 text-yellow-600" />
                </div>
                <h3 className="font-semibold text-gray-900 text-sm mb-1">Domain Risk</h3>
                <p className="text-xs text-gray-600">WHOIS data, domain age, registrar reputation</p>
              </div>
              
              <div className="bg-white rounded-lg p-4 border border-gray-200 text-center">
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <Users className="w-5 h-5 text-blue-600" />
                </div>
                <h3 className="font-semibold text-gray-900 text-sm mb-1">Business Risk</h3>
                <p className="text-xs text-gray-600">Company verification, legal compliance, sanctions</p>
              </div>
              
              <div className="bg-white rounded-lg p-4 border border-gray-200 text-center">
                <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <TrendingUp className="w-5 h-5 text-green-600" />
                </div>
                <h3 className="font-semibold text-gray-900 text-sm mb-1">Traffic Risk</h3>
                <p className="text-xs text-gray-600">Website traffic, popularity metrics, engagement</p>
              </div>
              
              <div className="bg-white rounded-lg p-4 border border-gray-200 text-center">
                <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <FileText className="w-5 h-5 text-purple-600" />
                </div>
                <h3 className="font-semibold text-gray-900 text-sm mb-1">Content Risk</h3>
                <p className="text-xs text-gray-600">Privacy policies, terms of service, legal compliance</p>
              </div>
            </div>
            
            {/* What You'll Get */}
            <div className="bg-white rounded-lg p-4 border border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
                <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
                What You'll Get
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                <div className="flex items-start space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                  <span className="text-gray-700">Comprehensive risk score (1-10)</span>
                </div>
                <div className="flex items-start space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                  <span className="text-gray-700">Detailed category breakdown</span>
                </div>
                <div className="flex items-start space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                  <span className="text-gray-700">Risk level classification</span>
                </div>
                <div className="flex items-start space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                  <span className="text-gray-700">Actionable recommendations</span>
                </div>
                <div className="flex items-start space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                  <span className="text-gray-700">Exportable PDF reports</span>
                </div>
                <div className="flex items-start space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                  <span className="text-gray-700">Historical assessment tracking</span>
                </div>
              </div>
            </div>
          </div>
        )}
        {assessmentPollingError && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800 flex flex-col items-start">
            <div className="font-semibold mb-1">Assessment could not complete</div>
            <div className="text-xs mb-2">{assessmentPollingError}</div>
            <button
              className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-xs"
              onClick={() => {
                setAssessmentPollingError(null);
                setIsAssessing(true);
                setShowProcessingMessage(true);
                const persistedDomain = localStorage.getItem('currentAssessmentDomain') || 'Unknown Domain';
                pollAssessment(currentAssessmentId, persistedDomain);
              }}
              disabled={isAssessing}
            >
              {isAssessing ? (
                <><RefreshCw className="w-3 h-3 mr-1 animate-spin" />Retrying...</>
              ) : (
                'Retry'
              )}
            </button>
          </div>
        )}

        {/* Main Content Grid - 2 columns, left column with 2 rows */}
        <div className="flex flex-row gap-6 items-stretch">
          {/* Left Column: vertical stack */}
          <div className="flex flex-col gap-6 w-full max-w-xs" style={{ flex: '0 0 35%' }}>
            {/* Tile 1: Assessment Hub */}
            {/* Assessment Hub (input, fetch, new assessment) */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center mb-6">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center mr-4">
                  <Shield className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-gray-900">Assessment Hub</h3>
                  <p className="text-sm text-gray-500">Enter a business domain to assess risk and compliance</p>
                </div>
              </div>

              {/* ENHANCED Domain Input with Instructions */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Business Website Domain *
                  </label>
                  
                  {/* Enhanced Input Field */}
                  <div className="relative">
                    <input
                      type="text"
                      value={domainInput}
                      onChange={(e) => setDomainInput(e.target.value)}
                      placeholder="shopify.com"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all pr-12"
                    />
                    <div className="absolute inset-y-0 right-0 flex items-center pr-3">
                      <Globe className="w-5 h-5 text-gray-400" />
                    </div>
                  </div>
                  
                  {/* Format Guidelines */}
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mt-3">
                    <div className="flex items-start space-x-2">
                      <Info className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                      <div className="text-xs text-blue-800">
                        <p className="font-medium mb-1">What to enter:</p>
                        <div className="grid grid-cols-2 gap-1 text-xs">
                          <div>
                            <span className="text-green-600">✓</span> shopify.com
                          </div>
                          <div>
                            <span className="text-green-600">✓</span> microsoft.com
                          </div>
                          <div>
                            <span className="text-red-600">✗</span> https://shopify.com
                          </div>
                          <div>
                            <span className="text-red-600">✗</span> Shopify Inc.
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Enhanced Action Buttons */}
                <div className="space-y-3">
                  {/* FIRST BUTTON: Fetch Existing Assessment */}
                  <button
                    onClick={handleFetchAssessment}
                    disabled={!domainInput.trim() || isFetching}
                    className="w-full border-2 border-blue-600 text-blue-600 py-3 px-4 rounded-lg hover:bg-blue-50 transition-colors disabled:opacity-50 flex items-center justify-center font-medium"
                  >
                    {isFetching ? (
                      <>
                        <RefreshCw className="w-5 h-5 mr-2 animate-spin" />
                        Searching Database...
                      </>
                    ) : (
                      <>
                        <Eye className="w-5 h-5 mr-2" />
                        Check Existing Assessment
                      </>
                    )}
                  </button>

                  {/* SECOND BUTTON: Create New Assessment */}
                  <button
                    onClick={handleStartAssessment}
                    disabled={!domainInput.trim() || isAssessing}
                    className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center justify-center font-medium"
                  >
                    {isAssessing ? (
                      assessmentProgress ? (
                        <>
                          <RefreshCw className="w-5 h-5 mr-2 animate-spin" />
                          {assessmentProgress.progress}% - {assessmentProgress.current_step}
                        </>
                      ) : (
                        <>
                          <RefreshCw className="w-5 h-5 mr-2 animate-spin" />
                          Starting Risk Analysis...
                        </>
                      )
                    ) : (
                      <>
                        <Search className="w-5 h-5 mr-2" />
                        Start New Risk Assessment
                      </>
                    )}
                  </button>
                </div>

                {/* Input Validation Hint */}
                {domainInput && !domainInput.includes('.') && (
                  <div className="flex items-center space-x-2 text-xs text-amber-600 bg-amber-50 border border-amber-200 rounded p-2">
                    <AlertTriangle className="w-4 h-4" />
                    <span>Please enter a valid domain (e.g., company.com)</span>
                  </div>
                )}
              </div>
            </div>

            {/* Recent Assessments */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 flex-1 overflow-y-auto">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900">Recent Assessments</h3>
                  <button 
                    onClick={() => {
                      loadRecentAssessments();
                      addToast('Refreshing assessments...', 'info');
                    }}
                    className="text-blue-600 hover:text-blue-700 p-1 rounded hover:bg-blue-50 transition-colors"
                    title="Refresh assessments"
                  >
                    <RefreshCw className="w-4 h-4" />
                  </button>
                </div>
              </div>
              
              {recentAssessments.length === 0 ? (
                <div className="p-6 text-center text-gray-500">
                  <Shield className="w-8 h-8 mx-auto mb-2 text-gray-300" />
                  <p>No assessments yet</p>
                </div>
              ) : (
                <div className="divide-y divide-gray-100">
                  {recentAssessments.map((assessment, index) => {
                    const status = getAssessmentStatus(assessment);
                    const isInProgress = inProgressAssessments.has(assessment.id);
                    const progress = globalProgress[assessment.id];
                    
                    return (
                      <div 
                        key={assessment.id || index}
                        onClick={() => selectAssessment(assessment)}
                        className={`p-4 hover:bg-gray-50 cursor-pointer transition-colors ${
                          isInProgress ? 'bg-blue-50 border-l-4 border-blue-400' : ''
                        }`}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-2">
                            <h4 className="font-medium text-gray-900 truncate">
                              {safeGetCompanyName(assessment)}
                            </h4>
                            {isInProgress && (
                              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                <RefreshCw className="w-3 h-3 mr-1 animate-spin" />
                                Processing
                              </span>
                            )}
                          </div>
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRiskBadgeColor(assessment.risk_assessment_data?.risk_level)}`}>
                            {assessment.risk_assessment_data?.risk_level || 'Medium'}
                          </span>
                        </div>
                        <div className="flex items-center justify-between text-sm text-gray-500">
                          <span>{new Date(assessment.created_at).toLocaleDateString()}</span>
                          <div className="flex items-center space-x-2">
                            {isInProgress && progress && (
                              <span className="text-xs text-blue-600">
                                {progress.progress || 0}%
                              </span>
                            )}
                            <span className="font-medium">
                              {assessment.risk_assessment_data?.weighted_total_score?.toFixed(1) || 'N/A'}
                            </span>
                          </div>
                        </div>
                        {isInProgress && progress && (
                          <div className="mt-2">
                            <div className="w-full bg-gray-200 rounded-full h-1">
                              <div 
                                className="bg-blue-600 h-1 rounded-full transition-all duration-300"
                                style={{ width: `${progress.progress || 0}%` }}
                              ></div>
                            </div>
                            <div className="text-xs text-gray-500 mt-1">
                              {progress.current_step || 'Processing...'}
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
          {/* Right Tile: 65% width */}
          <div className="flex-1 min-w-0" style={{ flex: '0 0 65%' }}>
            <div className="max-w-2xl mx-auto">
              {/* Infographic, results, or waiting message (was in right column) */}
              {/* ...copy from previous right column... */}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Assessment List View Component - FIXED TABLE
const AssessmentListView = ({ assessments, onSelectAssessment, onDeleteAssessment, onBulkDelete, addToast, setCurrentAssessmentId, setShowProcessingMessage, addInProgressAssessment }) => {
  const [selectedAssessments, setSelectedAssessments] = useState(new Set());
  const [selectAll, setSelectAll] = useState(false);

  const handleSelectAll = () => {
    if (selectAll) {
      setSelectedAssessments(new Set());
    } else {
      setSelectedAssessments(new Set(assessments.map(a => a.id)));
    }
    setSelectAll(!selectAll);
  };

  const handleSelectAssessment = (assessmentId) => {
    const newSelected = new Set(selectedAssessments);
    if (newSelected.has(assessmentId)) {
      newSelected.delete(assessmentId);
    } else {
      newSelected.add(assessmentId);
    }
    setSelectedAssessments(newSelected);
    setSelectAll(newSelected.size === assessments.length);
  };

  const handleBulkDelete = () => {
    if (selectedAssessments.size > 0) {
      const confirmed = window.confirm(`Delete ${selectedAssessments.size} assessments?`);
      if (confirmed) {
        onBulkDelete(Array.from(selectedAssessments));
        setSelectedAssessments(new Set());
        setSelectAll(false);
      }
    }
  };

  const getRiskBadgeColor = (risk) => {
    switch (risk?.toLowerCase()) {
      case 'low': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'high': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">All Risk Assessments</h3>
            <p className="text-sm text-gray-500">{assessments.length} total assessments</p>
          </div>
          <div className="flex items-center space-x-2">
            {selectedAssessments.size > 0 && (
              <button
                onClick={handleBulkDelete}
                className="flex items-center space-x-2 px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                <Trash2 className="w-4 h-4" />
                <span>Delete ({selectedAssessments.size})</span>
              </button>
            )}
            <button
              onClick={() => exportToCSV(assessments)}
              className="flex items-center space-x-2 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              <FileDown className="w-4 h-4" />
              <span>Export CSV</span>
            </button>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left">
                <button
                  onClick={handleSelectAll}
                  className="flex items-center text-gray-500 hover:text-gray-700"
                >
                  {selectAll ? <CheckSquare className="w-4 h-4" /> : <Square className="w-4 h-4" />}
                </button>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Company
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Business Domain
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Risk Level
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Score
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {assessments.map((assessment) => (
              <tr 
                key={assessment.id} 
                className={`hover:bg-gray-50 cursor-pointer ${selectedAssessments.has(assessment.id) ? 'bg-blue-50' : ''}`}
              >
                <td className="px-6 py-4 whitespace-nowrap">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleSelectAssessment(assessment.id);
                    }}
                    className="flex items-center text-gray-500 hover:text-gray-700"
                  >
                    {selectedAssessments.has(assessment.id) ? 
                      <CheckSquare className="w-4 h-4 text-blue-600" /> : 
                      <Square className="w-4 h-4" />
                    }
                  </button>
                </td>
                <td 
                  className="px-6 py-4 whitespace-nowrap cursor-pointer"
                  onClick={() => onSelectAssessment(assessment)}
                >
                  <div className="text-sm font-medium text-gray-900">{safeGetCompanyName(assessment)}</div>
                  <div className="text-sm text-gray-500">
                    Assessment
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <button
                    onClick={() => window.open(`https://${safeGetBusinessDomain(assessment)}`, '_blank')}
                    className="flex items-center text-blue-600 hover:text-blue-800 text-sm font-medium"
                  >
                    <Globe className="w-4 h-4 mr-1" />
                    {safeGetBusinessDomain(assessment)}
                    <ExternalLink className="w-3 h-3 ml-1" />
                  </button>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRiskBadgeColor(assessment.risk_assessment_data?.risk_level)}`}>
                    {assessment.risk_assessment_data?.risk_level || 'Medium'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="text-sm font-medium text-gray-900">
                      {assessment.risk_assessment_data?.weighted_total_score?.toFixed(1) || 'N/A'}
                    </div>
                    <div className="ml-2 w-16 bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${
                          (assessment.risk_assessment_data?.weighted_total_score || 0) >= 7 ? 'bg-green-500' : 
                          (assessment.risk_assessment_data?.weighted_total_score || 0) >= 4 ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${((assessment.risk_assessment_data?.weighted_total_score || 0) / 10) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadgeColor(getAssessmentStatus(assessment))}`}>
                    {getStatusIcon(getAssessmentStatus(assessment))}
                    <span className="ml-1">{getAssessmentStatus(assessment)}</span>
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date(assessment.created_at).toLocaleDateString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        copyToClipboard(assessment.id);
                        addToast('Assessment ID copied to clipboard!', 'success');
                      }}
                      className="text-gray-600 hover:text-gray-900 p-1 rounded"
                      title="Copy Assessment ID"
                    >
                      <Copy className="w-4 h-4" />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        generatePDFReport(assessment);
                      }}
                      className="text-blue-600 hover:text-blue-900 p-1 rounded"
                      title="Export PDF"
                    >
                      <Download className="w-4 h-4" />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectAssessment(assessment);
                      }}
                      className="text-green-600 hover:text-green-900 p-1 rounded"
                      title="View Details"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                    {getAssessmentStatus(assessment) === 'processing' && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          // Set this as the current assessment to check status
                          setCurrentAssessmentId(assessment.id);
                          setShowProcessingMessage(true);
                          addInProgressAssessment(assessment.id);
                          addToast(`Checking status for ${safeGetCompanyName(assessment)}`, 'info');
                        }}
                        className="text-blue-600 hover:text-blue-900 p-1 rounded"
                        title="Check Status"
                      >
                        <Activity className="w-4 h-4" />
                      </button>
                    )}
                    {getAssessmentStatus(assessment) === 'failed' && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          const confirmed = window.confirm(`Retry assessment for ${safeGetCompanyName(assessment)}?`);
                          if (confirmed) {
                            // TODO: Implement retry logic when backend supports it
                            addToast('Retry functionality coming soon!', 'info');
                          }
                        }}
                        className="text-blue-600 hover:text-blue-900 p-1 rounded"
                        title="Retry Assessment"
                      >
                        <RefreshCw className="w-4 h-4" />
                      </button>
                    )}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        const confirmed = window.confirm(`Delete assessment for ${safeGetCompanyName(assessment)}?`);
                        if (confirmed) {
                          onDeleteAssessment(assessment.id);
                        }
                      }}
                      className="text-red-600 hover:text-red-900 p-1 rounded"
                      title="Delete"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// Enhanced Risk Assessments Page
const RiskAssessmentsPage = () => {
  const [assessments, setAssessments] = useState([]);
  const [selectedAssessment, setSelectedAssessment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState('list'); // 'list' or 'detail'
  const [expandedSections, setExpandedSections] = useState({});

  // Add these hooks/utilities for AssessmentListView actions
  const { addToast } = useToast();
  const [currentAssessmentId, setCurrentAssessmentId] = useState(null);
  const [showProcessingMessage, setShowProcessingMessage] = useState(false);
  const { addInProgressAssessment } = useAssessmentState();

  useEffect(() => {
    loadAssessments();
  }, []);

  const loadAssessments = async () => {
    try {
      const data = await apiService.fetchAssessments();
      setAssessments(data);
    } catch (error) {
      console.error('Failed to load assessments:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectAssessment = (assessment) => {
    setSelectedAssessment(assessment);
    setView('detail');
  };

  const handleDeleteAssessment = async (assessmentId) => {
    try {
      await apiService.deleteAssessment(assessmentId);
      setAssessments(assessments.filter(a => a.id !== assessmentId));
    } catch (error) {
      alert('Failed to delete assessment');
    }
  };

  const handleBulkDelete = async (assessmentIds) => {
    try {
      // Call delete for each assessment
      await Promise.all(assessmentIds.map(id => apiService.deleteAssessment(id)));
      setAssessments(assessments.filter(a => !assessmentIds.includes(a.id)));
    } catch (error) {
      alert('Failed to delete assessments');
    }
  };

  const handleBackToList = () => {
    setView('list');
    setSelectedAssessment(null);
    setExpandedSections({});
  };

  const toggleSection = (sectionId) => {
    setExpandedSections(prev => ({
      ...prev,
      [sectionId]: !prev[sectionId]
    }));
  };

  // Helper functions for risk visualization
  const getRiskColor = (score) => {
    if (score >= 7) return 'text-green-600';
    if (score >= 4) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getRiskBgColor = (score) => {
    if (score >= 7) return 'bg-green-50';
    if (score >= 4) return 'bg-yellow-50';
    return 'bg-red-50';
  };

  const formatRiskCategory = (key) => {
    return key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-2 text-gray-600">Loading assessments...</span>
      </div>
    );
  }

  return (
    <div className="h-full">
      {view === 'list' ? (
        <div className="p-6">
          <AssessmentListView
            assessments={assessments}
            onSelectAssessment={handleSelectAssessment}
            onDeleteAssessment={handleDeleteAssessment}
            onBulkDelete={handleBulkDelete}
            addToast={addToast}
            setCurrentAssessmentId={setCurrentAssessmentId}
            setShowProcessingMessage={setShowProcessingMessage}
            addInProgressAssessment={addInProgressAssessment}
          />
        </div>
      ) : (
        <div className="p-6">
          <button
            onClick={handleBackToList}
            className="flex items-center text-blue-600 hover:text-blue-800 mb-4"
          >
            <ChevronRight className="w-4 h-4 mr-1 transform rotate-180" />
            Back to Assessments
          </button>
          
          {/* Detailed Assessment View with Expandable Categories */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-bold text-gray-900">
                Assessment Details - {safeGetCompanyName(selectedAssessment)}
              </h2>
              <p className="text-sm text-gray-500 mt-1">
                Created on {new Date(selectedAssessment?.created_at).toLocaleDateString()}
              </p>
            </div>
            
            {selectedAssessment ? (
              <div className="p-6">
                {/* Basic Information */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Company</label>
                    <p className="mt-1 text-lg font-semibold text-gray-900">{safeGetCompanyName(selectedAssessment)}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Domain</label>
                    <p className="mt-1 text-lg font-semibold text-gray-900">{selectedAssessment.domain || 'N/A'}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Overall Risk Level</label>
                    <p className={`mt-1 text-lg font-semibold ${
                      selectedAssessment.risk_assessment_data?.risk_level === 'Low' ? 'text-green-600' :
                      selectedAssessment.risk_assessment_data?.risk_level === 'Medium' ? 'text-yellow-600' :
                      'text-red-600'
                    }`}>
                      {selectedAssessment.risk_assessment_data?.risk_level || 'N/A'}
                    </p>
                  </div>
                </div>
                
                {/* Risk Categories - Expandable */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Categories Analysis</h3>
                  <div className="space-y-4">
                    {Object.entries(selectedAssessment.risk_assessment_data?.risk_categories || {}).map(([categoryKey, categoryData]) => (
                      <div key={categoryKey} className="border border-gray-200 rounded-lg">
                        <button
                          onClick={() => toggleSection(categoryKey)}
                          className="w-full p-4 text-left flex items-center justify-between hover:bg-gray-50 transition-colors"
                        >
                          <div className="flex items-center space-x-3">
                            <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${getRiskBgColor(categoryData.average_score)}`}>
                              {categoryKey === 'reputation_risk' && <TrendingUp className={`w-5 h-5 ${getRiskColor(categoryData.average_score)}`} />}
                              {categoryKey === 'financial_risk' && <DollarSign className={`w-5 h-5 ${getRiskColor(categoryData.average_score)}`} />}
                              {categoryKey === 'technology_risk' && <Lock className={`w-5 h-5 ${getRiskColor(categoryData.average_score)}`} />}
                              {categoryKey === 'business_risk' && <Building className={`w-5 h-5 ${getRiskColor(categoryData.average_score)}`} />}
                              {categoryKey === 'legal_compliance_risk' && <Scale className={`w-5 h-5 ${getRiskColor(categoryData.average_score)}`} />}
                            </div>
                            <div>
                              <h4 className="font-semibold text-gray-900">
                                {formatRiskCategory(categoryKey)}
                              </h4>
                              <p className="text-sm text-gray-500">
                                Score: {categoryData.average_score?.toFixed(1) || 'N/A'} • Weight: {Math.round(categoryData.weight * 100)}%
                              </p>
                            </div>
                          </div>
                          <ChevronDown className={`w-5 h-5 text-gray-400 transform transition-transform ${expandedSections[categoryKey] ? 'rotate-180' : ''}`} />
                        </button>
                        
                        {expandedSections[categoryKey] && (
                          <div className="p-4 pt-0">
                            <div className="space-y-3">
                              {categoryData.checks?.map((check, index) => (
                                <div key={index} className="bg-gray-50 rounded-lg p-3">
                                  <div className="flex items-center justify-between mb-2">
                                    <h5 className="font-medium text-gray-900">{check.check_name}</h5>
                                    <span className={`px-2 py-1 rounded text-sm font-medium ${getRiskBgColor(check.score)} ${getRiskColor(check.score)}`}>
                                      {check.score}/10
                                    </span>
                                  </div>
                                  <p className="text-sm text-gray-600">{check.reason}</p>
                                  {check.insight && (
                                    <p className="text-sm text-blue-600 mt-2">
                                      <Info className="w-4 h-4 inline mr-1" />
                                      {check.insight}
                                    </p>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Raw Scraper Data Section */}
                {selectedAssessment.scraped_data && (
                  <div className="bg-white rounded-xl shadow-sm border border-gray-200 mt-6">
                    <button
                      onClick={() => toggleSection('raw_scraper_data')}
                      className="w-full p-6 text-left flex items-center justify-between hover:bg-gray-50 transition-colors rounded-t-xl"
                    >
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center">
                          <Database className="w-6 h-6 text-indigo-600" />
                        </div>
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">Raw Scraper Data</h3>
                          <p className="text-sm text-gray-500">
                            {selectedAssessment.scraped_data.collection_summary?.successful_scrapers || 0} successful • 
                            {selectedAssessment.scraped_data.collection_summary?.failed_scrapers || 0} failed • 
                            {selectedAssessment.scraped_data.collection_summary?.success_rate || 0}% success rate
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="px-3 py-1 bg-indigo-100 text-indigo-600 rounded-full text-sm font-medium">
                          {Object.keys(selectedAssessment.scraped_data).filter(key => !key.startsWith('collection_') && !['domain', 'scrapers_attempted', 'scrapers_successful', 'scrapers_failed', 'collection_quality', 'execution_mode'].includes(key)).length} sources
                        </div>
                        {expandedSections['raw_scraper_data'] ? 
                          <ChevronUp className="w-5 h-5 text-gray-400" /> : 
                          <ChevronDown className="w-5 h-5 text-gray-400" />
                        }
                      </div>
                    </button>

                    {expandedSections['raw_scraper_data'] && (
                      <div className="px-6 pb-6 border-t border-gray-100">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                          {Object.entries(selectedAssessment.scraped_data).map(([scraperKey, scraperData]) => {
                            // Skip metadata fields
                            if (['collection_timestamp', 'domain', 'scrapers_attempted', 'scrapers_successful', 'scrapers_failed', 'collection_quality', 'execution_mode'].includes(scraperKey)) {
                              return null;
                            }

                            const isError = scraperData?.error;
                            const metadata = scraperData?._scraper_metadata;
                            const hasSourceUrl = metadata?.source_url;

                            return (
                              <div key={scraperKey} className={`border rounded-lg p-4 ${isError ? 'border-red-200 bg-red-50' : 'border-gray-200 bg-gray-50'}`}>
                                <div className="flex items-center justify-between mb-3">
                                  <div className="flex items-center space-x-2">
                                    <div className={`w-3 h-3 rounded-full ${isError ? 'bg-red-500' : 'bg-green-500'}`}></div>
                                    <h4 className="font-semibold text-gray-900 capitalize">
                                      {scraperKey.replace(/_/g, ' ')}
                                    </h4>
                                  </div>
                                  {hasSourceUrl && (
                                    <button
                                      onClick={() => window.open(metadata.source_url, '_blank')}
                                      className="flex items-center space-x-1 text-blue-600 hover:text-blue-800 text-sm"
                                      title={`View source: ${metadata.source_url}`}
                                    >
                                      <ExternalLink className="w-4 h-4" />
                                      <span>Source</span>
                                    </button>
                                  )}
                                </div>

                                {metadata && (
                                  <div className="text-xs text-gray-600 mb-2">
                                    <div className="flex items-center justify-between">
                                      <span>{metadata.description}</span>
                                      <span>{metadata.execution_time}s</span>
                                    </div>
                                    <div className="flex items-center justify-between mt-1">
                                      <span className={`px-2 py-0.5 rounded text-xs ${
                                        metadata.quality === 'high' ? 'bg-green-100 text-green-700' :
                                        metadata.quality === 'low' ? 'bg-yellow-100 text-yellow-700' :
                                        'bg-red-100 text-red-700'
                                      }`}>
                                        {metadata.quality} quality
                                      </span>
                                      <span className="text-gray-500">
                                        {new Date(metadata.timestamp).toLocaleTimeString()}
                                      </span>
                                    </div>
                                  </div>
                                )}

                                {isError ? (
                                  <div className="text-sm text-red-700">
                                    <p className="font-medium">Error:</p>
                                    <p className="mt-1">{scraperData.error}</p>
                                  </div>
                                ) : (
                                  <div className="space-y-2">
                                    <button
                                      onClick={() => toggleSection(`scraper_${scraperKey}`)}
                                      className="flex items-center space-x-1 text-sm text-gray-600 hover:text-gray-800"
                                    >
                                      {expandedSections[`scraper_${scraperKey}`] ? 
                                        <ChevronUp className="w-4 h-4" /> : 
                                        <ChevronDown className="w-4 h-4" />
                                      }
                                      <span>View Raw Data</span>
                                    </button>

                                    {expandedSections[`scraper_${scraperKey}`] && (
                                      <div className="mt-2 p-3 bg-white rounded border">
                                        <ExpandableDataView data={scraperData} label={scraperKey} />
                                      </div>
                                    )}

                                    {/* Show key data points for quick reference */}
                                    <div className="text-sm text-gray-700">
                                      {scraperKey === 'https_check' && scraperData.has_https !== undefined && (
                                        <p><span className="font-medium">HTTPS:</span> {scraperData.has_https ? '✅ Enabled' : '❌ Disabled'}</p>
                                      )}
                                      {scraperKey === 'whois_data' && scraperData.registrar && (
                                        <p><span className="font-medium">Registrar:</span> {scraperData.registrar}</p>
                                      )}
                                      {scraperKey === 'google_safe_browsing' && scraperData['Current Status'] && (
                                        <p><span className="font-medium">Status:</span> {scraperData['Current Status']}</p>
                                      )}
                                      {scraperKey === 'ssl_org_report' && scraperData.report_summary?.ssl_grade && (
                                        <p><span className="font-medium">SSL Grade:</span> {scraperData.report_summary.ssl_grade}</p>
                                      )}
                                      {scraperKey === 'ofac_sanctions' && scraperData.sanctions_screening && (
                                        <p><span className="font-medium">OFAC Status:</span> {scraperData.sanctions_screening.status}</p>
                                      )}
                                      {scraperKey === 'tranco_ranking' && scraperData['Tranco Rank'] && (
                                        <p><span className="font-medium">Rank:</span> {scraperData['Tranco Rank']}</p>
                                      )}
                                      {scraperKey === 'industry_classification' && scraperData.industry_category && (
                                        <p><span className="font-medium">Industry:</span> {scraperData.industry_category}</p>
                                      )}
                                    </div>
                                  </div>
                                )}
                              </div>
                            );
                          })}
                        </div>

                        {/* Collection Summary */}
                        {selectedAssessment.scraped_data.collection_summary && (
                          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                            <h4 className="font-semibold text-blue-900 mb-2">Collection Summary</h4>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                              <div>
                                <p className="text-blue-700 font-medium">Total Scrapers</p>
                                <p className="text-blue-900">{selectedAssessment.scraped_data.collection_summary.total_scrapers}</p>
                              </div>
                              <div>
                                <p className="text-green-700 font-medium">Successful</p>
                                <p className="text-green-900">{selectedAssessment.scraped_data.collection_summary.successful_scrapers}</p>
                              </div>
                              <div>
                                <p className="text-red-700 font-medium">Failed</p>
                                <p className="text-red-900">{selectedAssessment.scraped_data.collection_summary.failed_scrapers}</p>
                              </div>
                              <div>
                                <p className="text-blue-700 font-medium">Success Rate</p>
                                <p className="text-blue-900">{selectedAssessment.scraped_data.collection_summary.success_rate}%</p>
                              </div>
                            </div>
                            <div className="mt-3 text-sm">
                              <p className="text-blue-700">
                                <span className="font-medium">Quality Level:</span> 
                                <span className={`ml-1 px-2 py-0.5 rounded text-xs ${
                                  selectedAssessment.scraped_data.collection_summary.quality_level === 'EXCELLENT' ? 'bg-green-100 text-green-700' :
                                  selectedAssessment.scraped_data.collection_summary.quality_level === 'GOOD' ? 'bg-blue-100 text-blue-700' :
                                  'bg-yellow-100 text-yellow-700'
                                }`}>
                                  {selectedAssessment.scraped_data.collection_summary.quality_level}
                                </span>
                              </p>
                              <p className="text-blue-700 mt-1">
                                <span className="font-medium">Execution Mode:</span> {selectedAssessment.scraped_data.execution_mode || 'sequential_complete'}
                              </p>
                              <p className="text-blue-700 mt-1">
                                <span className="font-medium">Collection Time:</span> {new Date(selectedAssessment.scraped_data.collection_summary.collection_time).toLocaleString()}
                              </p>
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <p className="text-gray-600 p-6">No assessment selected.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

// Analytics Page
const AnalyticsPage = () => {
  const [analytics, setAnalytics] = useState({
    totalAssessments: 0,
    riskDistribution: { Low: 0, Medium: 0, High: 0, Unknown: 0 },
    averageScore: 0,
    statistics: {},
    loading: true
  });
  const [assessments, setAssessments] = useState([]);
  const [timeframe, setTimeframe] = useState('30'); // days
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalyticsData();
  }, [timeframe]);

  const loadAnalyticsData = async () => {
    setLoading(true);
    try {
      // Use the correct API service method
      const riskStats = await apiService.getRiskDistribution();
      
      // Get all assessments for additional analytics
      const allAssessments = await apiService.fetchAssessments();
      
      // Process assessments data
      const processedData = processAssessmentsData(allAssessments, parseInt(timeframe));
      
      setAnalytics({
        ...riskStats,
        ...processedData,
        loading: false
      });
      
      setAssessments(allAssessments);
    } catch (error) {
      console.error('Failed to load analytics:', error);
      
      // Fallback to processing assessments only
      try {
        const allAssessments = await apiService.fetchAssessments();
        const processedData = processAssessmentsData(allAssessments, parseInt(timeframe));
        
        setAnalytics({
          totalAssessments: allAssessments.length,
          riskDistribution: processedData.riskDistribution || { Low: 0, Medium: 0, High: 0, Unknown: 0 },
          averageScore: processedData.averageScore || 0,
          ...processedData,
          loading: false
        });
        
        setAssessments(allAssessments);
      } catch (fallbackError) {
        console.error('Fallback analytics load failed:', fallbackError);
        setAnalytics(prev => ({ ...prev, loading: false }));
      }
    } finally {
      setLoading(false);
    }
  };

  const processAssessmentsData = (assessments, days) => {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);
    
    const recentAssessments = assessments.filter(assessment => 
      new Date(assessment.created_at) >= cutoffDate
    );
    
    // Calculate risk distribution
    const riskDistribution = { Low: 0, Medium: 0, High: 0, Unknown: 0 };
    let totalScore = 0;
    let scoreCount = 0;
    
    // Calculate daily assessments for chart
    const dailyData = {};
    const scoreDistribution = { '0-3': 0, '3-5': 0, '5-7': 0, '7-10': 0 };
    
    recentAssessments.forEach(assessment => {
      const date = new Date(assessment.created_at).toISOString().split('T')[0];
      const score = assessment.risk_assessment_data?.weighted_total_score || 0;
      const riskLevel = assessment.risk_assessment_data?.risk_level || 'Unknown';
      
      // Risk distribution
      riskDistribution[riskLevel] = (riskDistribution[riskLevel] || 0) + 1;
      
      // Average score calculation
      if (score > 0) {
        totalScore += score;
        scoreCount++;
      }
      
      // Daily data
      if (!dailyData[date]) {
        dailyData[date] = { date, total: 0, Low: 0, Medium: 0, High: 0, Unknown: 0 };
      }
      dailyData[date].total++;
      dailyData[date][riskLevel]++;
      
      // Score distribution
      if (score < 3) scoreDistribution['0-3']++;
      else if (score < 5) scoreDistribution['3-5']++;
      else if (score < 7) scoreDistribution['5-7']++;
      else scoreDistribution['7-10']++;
    });
    
    const dailyAssessments = Object.values(dailyData).sort((a, b) => 
      new Date(a.date) - new Date(b.date)
    );
    
    return {
      recentAssessments: recentAssessments.length,
      riskDistribution,
      averageScore: scoreCount > 0 ? totalScore / scoreCount : 0,
      dailyAssessments,
      scoreDistribution,
      avgResponseTime: '45s',
      completionRate: Math.round((recentAssessments.length / Math.max(assessments.length, 1)) * 100)
    };
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-2 text-gray-600">Loading analytics...</span>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h1>
        <div className="flex items-center space-x-4">
          <select
            value={timeframe}
            onChange={(e) => setTimeframe(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
          >
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 90 days</option>
          </select>
          <button
            onClick={loadAnalyticsData}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Assessments</p>
              <p className="text-3xl font-bold text-gray-900">{analytics.totalAssessments || analytics.total_assessments || 0}</p>
              <p className="text-sm text-gray-500">All time</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <BarChart3 className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Recent Assessments</p>
              <p className="text-3xl font-bold text-gray-900">{analytics.recentAssessments || 0}</p>
              <p className="text-sm text-gray-500">Last {timeframe} days</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Average Score</p>
              <p className="text-3xl font-bold text-gray-900">{(analytics.averageScore || analytics.average_score || 0).toFixed(1)}</p>
              <p className="text-sm text-gray-500">Out of 10</p>
            </div>
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <PieChart className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">High Risk</p>
              <p className="text-3xl font-bold text-red-600">{(analytics.riskDistribution || analytics.risk_distribution)?.High || 0}</p>
              <p className="text-sm text-gray-500">Requires attention</p>
            </div>
            <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-6 h-6 text-red-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Risk Distribution Chart */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
          <PieChart className="w-5 h-5 mr-2 text-blue-600" />
          Risk Distribution Overview
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {Object.entries((analytics.riskDistribution || analytics.risk_distribution) || {}).map(([risk, count]) => (
            <div key={risk} className="text-center p-4 rounded-lg border border-gray-200">
              <div className={`w-16 h-16 rounded-full mx-auto mb-3 flex items-center justify-center text-2xl font-bold ${
                risk === 'Low' ? 'bg-green-100 text-green-600' :
                risk === 'Medium' ? 'bg-yellow-100 text-yellow-600' :
                risk === 'High' ? 'bg-red-100 text-red-600' : 'bg-gray-100 text-gray-600'
              }`}>
                {count}
              </div>
              <h4 className="font-semibold text-gray-900">{risk} Risk</h4>
              <p className="text-sm text-gray-500">
                {Math.round((count / Math.max((analytics.totalAssessments || analytics.total_assessments) || 1, 1)) * 100)}% of total
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Export Options */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Download className="w-5 h-5 mr-2 text-blue-600" />
          Export Analytics
        </h3>
        <div className="flex items-center space-x-4">
          <button
            onClick={() => apiService.exportData('csv')}
            className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <FileDown className="w-4 h-4" />
            <span>Export Summary CSV</span>
          </button>
          <button
            onClick={() => apiService.exportData('csv')}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <FileDown className="w-4 h-4" />
            <span>Export Detailed CSV</span>
          </button>
          <span className="text-sm text-gray-500">
            Analytics data for the last {timeframe} days
          </span>
        </div>
      </div>
    </div>
  );
};

// Settings Page
const SettingsPage = () => {
  const [apiHealth, setApiHealth] = useState('checking');
  const [settings, setSettings] = useState({
    notifications: true,
    autoRefresh: false,
    theme: 'light'
  });

  useEffect(() => {
    checkApiHealth();
  }, []);

  const checkApiHealth = async () => {
    try {
      await apiService.checkBackendHealth();
      setApiHealth('connected');
    } catch (error) {
      setApiHealth('disconnected');
    }
  };

  const handleSettingChange = (setting, value) => {
    setSettings(prev => ({
      ...prev,
      [setting]: value
    }));
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
      
      {/* API Health Status */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Activity className="w-5 h-5 mr-2 text-blue-600" />
          API Health Status
        </h3>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`w-3 h-3 rounded-full ${
              apiHealth === 'connected' ? 'bg-green-500' :
              apiHealth === 'disconnected' ? 'bg-red-500' : 'bg-yellow-500'
            }`}></div>
            <span className="text-sm font-medium text-gray-900">
              Backend API: {apiHealth === 'connected' ? 'Connected' : 
                          apiHealth === 'disconnected' ? 'Disconnected' : 'Checking...'}
            </span>
          </div>
          <button
            onClick={checkApiHealth}
            className="flex items-center space-x-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Check Status</span>
          </button>
        </div>
        <div className="mt-4 text-sm text-gray-500">
          <p>API Endpoint: {apiService.baseURL}</p>
          <p>Last checked: {new Date().toLocaleTimeString()}</p>
        </div>
      </div>

      {/* Application Settings */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Settings className="w-5 h-5 mr-2 text-blue-600" />
          Application Settings
        </h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-900">Enable Notifications</label>
              <p className="text-sm text-gray-500">Receive alerts for high-risk assessments</p>
            </div>
            <button
              onClick={() => handleSettingChange('notifications', !settings.notifications)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                settings.notifications ? 'bg-blue-600' : 'bg-gray-200'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  settings.notifications ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-900">Auto-refresh Data</label>
              <p className="text-sm text-gray-500">Automatically refresh assessment data</p>
            </div>
            <button
              onClick={() => handleSettingChange('autoRefresh', !settings.autoRefresh)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                settings.autoRefresh ? 'bg-blue-600' : 'bg-gray-200'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  settings.autoRefresh ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-900">Theme</label>
              <p className="text-sm text-gray-500">Choose your preferred theme</p>
            </div>
            <select
              value={settings.theme}
              onChange={(e) => handleSettingChange('theme', e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
            >
              <option value="light">Light</option>
              <option value="dark">Dark</option>
              <option value="auto">Auto</option>
            </select>
          </div>
        </div>
      </div>

      {/* System Information */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Info className="w-5 h-5 mr-2 text-blue-600" />
          System Information
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Application Version</label>
            <p className="mt-1 text-sm text-gray-900">v3.0.0</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Assessment Type</label>
            <p className="mt-1 text-sm text-gray-900">Unified (AI + Scrapers)</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Database</label>
            <p className="mt-1 text-sm text-gray-900">Supabase</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">AI Model</label>
            <p className="mt-1 text-sm text-gray-900">Gemini 1.5 Flash</p>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Zap className="w-5 h-5 mr-2 text-blue-600" />
          Quick Actions
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={() => window.open(apiService.baseURL + '/docs', '_blank')}
            className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <FileText className="w-5 h-5 text-blue-600" />
            <div className="text-left">
              <div className="font-medium text-gray-900">API Documentation</div>
              <div className="text-sm text-gray-500">View API endpoints and documentation</div>
            </div>
          </button>
          
          <button
            onClick={() => apiService.exportData('csv')}
            className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Download className="w-5 h-5 text-green-600" />
            <div className="text-left">
              <div className="font-medium text-gray-900">Export All Data</div>
              <div className="text-sm text-gray-500">Download complete assessment data</div>
            </div>
          </button>
          
          <button
            onClick={checkApiHealth}
            className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Activity className="w-5 h-5 text-purple-600" />
            <div className="text-left">
              <div className="font-medium text-gray-900">System Health Check</div>
              <div className="text-sm text-gray-500">Verify all system components</div>
            </div>
          </button>
          
          <button
            onClick={() => window.location.reload()}
            className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <RefreshCw className="w-5 h-5 text-orange-600" />
            <div className="text-left">
              <div className="font-medium text-gray-900">Refresh Application</div>
              <div className="text-sm text-gray-500">Reload the entire application</div>
            </div>
          </button>
        </div>
      </div>

      {/* Support & Help */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Mail className="w-5 h-5 mr-2 text-blue-600" />
          Support & Help
        </h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium text-gray-900">Need Help?</div>
              <div className="text-sm text-gray-500">Contact the development team for support</div>
            </div>
            <button
              onClick={() => window.open('mailto:bidya.bibhu@chargebee.com?subject=KYB System Support', '_blank')}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Mail className="w-4 h-4" />
              <span>Contact Support</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Main App Component
// Update the Main App Component in App.js to handle auth state

// Main App Component
const App = () => {
  const [user, setUser] = useState(null);
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);

  // Check for existing session on mount
  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      // Check if we have a stored token
      const token = localStorage.getItem('auth_token');
      const storedUser = localStorage.getItem('user_data');
      
      if (token && storedUser) {
        // Verify token is still valid
        const currentUser = await apiService.getCurrentUser();
        if (currentUser) {
          setUser(currentUser);
        } else {
          // Token expired or invalid
          apiService.clearAuthTokens();
        }
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      apiService.clearAuthTokens();
    } finally {
      setIsCheckingAuth(false);
    }
  };

  const handleLogin = async (email, password) => {
    try {
      // Call login API
      const response = await apiService.login(email, password);
      
      if (response.success) {
        // Successful login
        setUser(response.user);
        return { success: true };
      } else {
        return { success: false, message: response.message || 'Invalid email or password' };
      }
    } catch (error) {
      return { success: false, message: error.message || 'Invalid email or password' };
    }
  };

  const handleLogout = async () => {
    try {
      await apiService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setCurrentPage('dashboard');
    }
  };

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <ChargebeeStyleDashboard />;
      case 'assessments':
        return <RiskAssessmentsPage />;
      case 'analytics':
        return <AnalyticsPage />;
      case 'settings':
        return <SettingsPage />;
      default:
        return <ChargebeeStyleDashboard />;
    }
  };

  // Show loading screen while checking auth
  if (isCheckingAuth) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <LoginPage onLogin={handleLogin} />;
  }

  return (
    <ToastProvider>
      <div className="h-screen flex flex-col bg-gray-50">
        <Header user={user} onLogout={handleLogout} />
        <div className="flex flex-1 overflow-hidden">
          <Sidebar currentPage={currentPage} onPageChange={setCurrentPage} />
          <main className="flex-1 overflow-auto">
            {renderCurrentPage()}
          </main>
        </div>
      </div>
    </ToastProvider>
  );
};

export default App;