import React, { useState, useEffect } from 'react';
import { 
  User, LogOut, FileText, BarChart3, Settings, Shield, TrendingUp, 
  Users, Database, Eye, PieChart, Calendar, Search, Plus, Filter, 
  Download, AlertTriangle, CheckCircle, XCircle, Clock, Activity,
  Globe, DollarSign, Lock, Building, Scale, RefreshCw, ExternalLink,
  Home, ChevronRight, Mail, Bell, ChevronDown, ChevronUp, Info,
  Zap, ShieldCheck, Trash2, FileDown, CheckSquare, Square,
  Edit3, Copy, Share2
} from 'lucide-react';

// Import the API service - FIXED IMPORT
import apiService from './services/api';
import ConnectionStatus from './components/ConnectionStatus';

// Mock user for demonstration
const mockUser = {
  email: 'bidya.bibhu@chargebee.com',
  name: 'Bidya Sharma',
  role: 'Risk Analyst'
};

// Utility functions for export
const generatePDFReport = (assessment) => {
  if (assessment.id) {
    apiService.generatePDFReport(assessment.id)
      .then(result => {
        console.log('PDF generation result:', result);
        alert(`PDF report for ${assessment.company_name} generated successfully!`);
      })
      .catch(error => {
        console.error('PDF generation failed:', error);
        alert(`Failed to generate PDF: ${error.message}`);
      });
  } else {
    alert(`PDF report for ${assessment.company_name} would be generated here. Assessment ID required.`);
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
        assessment.company_name,
        assessment.domain || 'N/A',
        assessment.risk_assessment_data?.risk_level || 'N/A',
        assessment.risk_assessment_data?.weighted_total_score?.toFixed(1) || 'N/A',
        new Date(assessment.created_at).toLocaleDateString(),
        assessment.assessment_type === 'enhanced_with_scrapers' ? 'Enhanced' : 'Standard'
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

// Login Component
const LoginPage = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    setTimeout(() => {
      onLogin({
        email,
        name: email.split('@')[0].replace('.', ' ').replace(/\b\w/g, l => l.toUpperCase()),
        role: 'Risk Analyst'
      });
      setIsLoading(false);
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md border border-gray-100">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-full mb-4 shadow-lg">
            <Shield className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Chargebee KYB</h1>
          <p className="text-gray-600">Risk Assessment Platform</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Chargebee Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your.name@chargebee.com"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              required
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-3 px-4 rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all font-semibold disabled:opacity-50 flex items-center justify-center"
          >
            {isLoading ? (
              <>
                <RefreshCw className="w-5 h-5 mr-2 animate-spin" />
                Signing In...
              </>
            ) : (
              'Sign In'
            )}
          </button>
        </form>
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
              <h1 className="text-xl font-bold text-gray-900">Chargebee KYB Platform</h1>
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

  // Load data on component mount
  useEffect(() => {
    loadRecentAssessments();
  }, []);

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

  // FIXED: Handle NEW assessment (Create new assessment)
  const handleStartAssessment = async () => {
    if (!domainInput.trim()) return;
    
    setIsAssessing(true);
    try {
      console.log(`🚀 Creating NEW assessment for: ${domainInput}`);
      const result = await apiService.createAssessment(domainInput);
      setCurrentAssessment(result);
      setDomainInput('');
      setTimeout(loadRecentAssessments, 2000);
    } catch (error) {
      alert(`New assessment failed: ${error.message}`);
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
      if (result) {
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
        {/* CONNECTION STATUS - ADDED HERE */}
        <div className="mb-6">
          <ConnectionStatus />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-12 gap-6">
          
          {/* Left Panel - 30% */}
          <div className="col-span-12 lg:col-span-4 space-y-6">
            
            {/* Assessment Hub */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center mb-6">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center mr-4">
                  <Shield className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-gray-900">Assessment Hub</h3>
                  <p className="text-sm text-gray-500">Enter a domain to assess business risk</p>
                </div>
              </div>

              {/* Domain Input */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Website*</label>
                  <input
                    type="text"
                    value={domainInput}
                    onChange={(e) => setDomainInput(e.target.value)}
                    placeholder="shopify.com"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  />
                </div>

                {/* FIXED Action Buttons */}
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
                        Fetching Existing...
                      </>
                    ) : (
                      <>
                        <Eye className="w-5 h-5 mr-2" />
                        Fetch Existing Assessment
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
                      <>
                        <RefreshCw className="w-5 h-5 mr-2 animate-spin" />
                        Creating New Assessment...
                      </>
                    ) : (
                      <>
                        <Search className="w-5 h-5 mr-2" />
                        Start New Assessment
                      </>
                    )}
                  </button>
                </div>

                <p className="text-xs text-gray-500 text-center">
                  Fetch existing first, or create new assessment
                </p>
              </div>
            </div>

            {/* Recent Assessments */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900">Recent Assessments</h3>
                  <button 
                    onClick={loadRecentAssessments}
                    className="text-blue-600 hover:text-blue-700 p-1 rounded"
                  >
                    <RefreshCw className="w-4 h-4" />
                  </button>
                </div>
              </div>
              
              <div className="max-h-96 overflow-y-auto">
                {recentAssessments.length === 0 ? (
                  <div className="p-6 text-center text-gray-500">
                    <Shield className="w-8 h-8 mx-auto mb-2 text-gray-300" />
                    <p>No assessments yet</p>
                  </div>
                ) : (
                  <div className="divide-y divide-gray-100">
                    {recentAssessments.map((assessment, index) => (
                      <div 
                        key={assessment.id || index}
                        onClick={() => selectAssessment(assessment)}
                        className="p-4 hover:bg-gray-50 cursor-pointer transition-colors"
                      >
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-gray-900 truncate">
                            {assessment.company_name}
                          </h4>
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRiskBadgeColor(assessment.risk_assessment_data?.risk_level)}`}>
                            {assessment.risk_assessment_data?.risk_level || 'Medium'}
                          </span>
                        </div>
                        <div className="flex items-center justify-between text-sm text-gray-500">
                          <span>{new Date(assessment.created_at).toLocaleDateString()}</span>
                          <span className="font-medium">
                            {assessment.risk_assessment_data?.weighted_total_score?.toFixed(1) || 'N/A'}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Right Panel - 70% */}
          <div className="col-span-12 lg:col-span-8">
            {currentAssessment ? (
              <div className="space-y-6">
                
                {/* Assessment Header */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center space-x-4">
                      <div>
                        <h2 className="text-2xl font-bold text-gray-900 flex items-center">
                          {currentAssessment.domain || `${currentAssessment.company_name.toLowerCase()}.com`}
                          <ExternalLink 
                            className="w-5 h-5 ml-2 text-gray-400 cursor-pointer hover:text-blue-600" 
                            onClick={() => window.open(`https://${currentAssessment.domain || `${currentAssessment.company_name.toLowerCase()}.com`}`, '_blank')}
                          />
                        </h2>
                        <p className="text-gray-600">{currentAssessment.company_name}</p>
                        <p className="text-sm text-gray-500">
                          Assessment generated on {new Date(currentAssessment.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <button 
                      onClick={() => generatePDFReport(currentAssessment)}
                      className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      <Download className="w-4 h-4" />
                      <span>Export PDF</span>
                    </button>
                  </div>

                  {/* Risk Score Display */}
                  <div className="flex items-center justify-center py-8">
                    <div className="text-center">
                      <div className={`inline-flex items-center justify-center w-32 h-32 rounded-full text-4xl font-bold border-8 ${getRiskBgColor(currentAssessment.risk_assessment_data?.weighted_total_score)} ${getRiskBorderColor(currentAssessment.risk_assessment_data?.weighted_total_score)} ${getRiskColor(currentAssessment.risk_assessment_data?.weighted_total_score)}`}>
                        {currentAssessment.risk_assessment_data?.weighted_total_score?.toFixed(0) || 'N/A'}
                      </div>
                      <div className={`mt-4 px-4 py-2 rounded-full text-lg font-bold ${getRiskBgColor(currentAssessment.risk_assessment_data?.weighted_total_score)} ${getRiskColor(currentAssessment.risk_assessment_data?.weighted_total_score)}`}>
                        {getRiskLevel(currentAssessment.risk_assessment_data?.weighted_total_score)}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Risk Factor Breakdown */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-6">Risk Factor Breakdown</h3>
                  
                  <div className="grid grid-cols-3 gap-4 mb-6">
                    {Object.entries(currentAssessment.risk_assessment_data?.risk_categories || {}).slice(0, 6).map(([key, category], index) => {
                      const icons = [
                        TrendingUp, DollarSign, Lock, Building, Scale, FileText
                      ];
                      const IconComponent = icons[index] || FileText;
                      
                      return (
                        <div key={key} className="text-center p-4 rounded-lg border border-gray-200">
                          <div className={`w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-2 ${getRiskBgColor(category.average_score)}`}>
                            <IconComponent className={`w-6 h-6 ${getRiskColor(category.average_score)}`} />
                          </div>
                          <div className={`text-2xl font-bold ${getRiskColor(category.average_score)}`}>
                            {category.average_score?.toFixed(0) || 'N/A'}
                          </div>
                          <div className="text-xs text-gray-500 mt-1">
                            {formatRiskCategory(key).replace(' Risk', '')}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Detailed Categories */}
                <div className="space-y-4">
                  {Object.entries(currentAssessment.risk_assessment_data?.risk_categories || {}).map(([categoryKey, categoryData]) => (
                    <div key={categoryKey} className="bg-white rounded-xl shadow-sm border border-gray-200">
                      <button
                        onClick={() => toggleSection(categoryKey)}
                        className="w-full p-6 text-left flex items-center justify-between hover:bg-gray-50 transition-colors rounded-t-xl"
                      >
                        <div className="flex items-center space-x-4">
                          <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${getRiskBgColor(categoryData.average_score)}`}>
                            {categoryKey === 'reputation_risk' && <TrendingUp className={`w-6 h-6 ${getRiskColor(categoryData.average_score)}`} />}
                            {categoryKey === 'financial_risk' && <DollarSign className={`w-6 h-6 ${getRiskColor(categoryData.average_score)}`} />}
                            {categoryKey === 'technology_risk' && <Lock className={`w-6 h-6 ${getRiskColor(categoryData.average_score)}`} />}
                            {categoryKey === 'business_risk' && <Building className={`w-6 h-6 ${getRiskColor(categoryData.average_score)}`} />}
                            {categoryKey === 'legal_compliance_risk' && <Scale className={`w-6 h-6 ${getRiskColor(categoryData.average_score)}`} />}
                          </div>
                          <div>
                            <h3 className="text-lg font-semibold text-gray-900">
                              {formatRiskCategory(categoryKey)}
                            </h3>
                            <p className="text-sm text-gray-500">
                              Weight: {Math.round(categoryData.weight * 100)}% • Score: {categoryData.average_score?.toFixed(1)}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <div className={`px-3 py-1 rounded-full text-sm font-medium ${getRiskBgColor(categoryData.average_score)} ${getRiskColor(categoryData.average_score)}`}>
                            {categoryData.average_score?.toFixed(1)}
                          </div>
                          {expandedSections[categoryKey] ? 
                            <ChevronUp className="w-5 h-5 text-gray-400" /> : 
                            <ChevronDown className="w-5 h-5 text-gray-400" />
                          }
                        </div>
                      </button>

                      {expandedSections[categoryKey] && (
                        <div className="px-6 pb-6 border-t border-gray-100">
                          <div className="space-y-4 mt-4">
                            {categoryData.checks?.map((check, index) => (
                              <div key={index} className="bg-gray-50 rounded-lg p-4">
                                <div className="flex items-center justify-between mb-2">
                                  <h4 className="font-semibold text-gray-900">{check.check_name}</h4>
                                  <div className={`px-2 py-1 rounded text-sm font-medium ${getRiskBgColor(check.score)} ${getRiskColor(check.score)}`}>
                                    {check.score}/10
                                  </div>
                                </div>
                                <p className="text-sm text-gray-600 mb-2">{check.reason}</p>
                                {check.insight && (
                                  <p className="text-sm text-blue-600 bg-blue-50 p-2 rounded border-l-4 border-blue-200">
                                    <Info className="w-4 h-4 inline mr-1" />
                                    {check.insight}
                                  </p>
                                )}
                                <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
                                  <span>Source: {check.source}</span>
                                  <span className={`flex items-center ${check.public_data_available ? 'text-green-600' : 'text-red-600'}`}>
                                    {check.public_data_available ? <CheckCircle className="w-3 h-3 mr-1" /> : <AlertTriangle className="w-3 h-3 mr-1" />}
                                    {check.public_data_available ? 'Data Available' : 'No Public Data'}
                                  </span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              /* Empty State */
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
                <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <Shield className="w-10 h-10 text-gray-400" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">No Assessment Selected</h3>
                <p className="text-gray-600 mb-6">Enter a domain in the Assessment Hub to get started, or select from recent assessments.</p>
                <div className="flex items-center justify-center space-x-4 text-sm text-gray-500">
                  <div className="flex items-center">
                    <Clock className="w-4 h-4 mr-1" />
                    <span>Assessment takes 30-60 seconds</span>
                  </div>
                  <span>•</span>
                  <div className="flex items-center">
                    <Globe className="w-4 h-4 mr-1" />
                    <span>Real-time data collection</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Assessment List View Component
const AssessmentListView = ({ assessments, onSelectAssessment, onDeleteAssessment, onBulkDelete }) => {
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

  const getBusinessDomain = (assessment) => {
    return assessment.domain || `${assessment.company_name.toLowerCase().replace(' ', '')}.com`;
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
                  <div className="text-sm font-medium text-gray-900">{assessment.company_name}</div>
                  <div className="text-sm text-gray-500">
                    {assessment.assessment_type === 'enhanced_with_scrapers' ? 'Enhanced' : 
                     assessment.assessment_type === 'unified_ai_plus_scrapers' ? 'Unified' : 'Standard'} Assessment
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <button
                    onClick={() => window.open(`https://${getBusinessDomain(assessment)}`, '_blank')}
                    className="flex items-center text-blue-600 hover:text-blue-800 text-sm font-medium"
                  >
                    <Globe className="w-4 h-4 mr-1" />
                    {getBusinessDomain(assessment)}
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
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date(assessment.created_at).toLocaleDateString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div className="flex items-center space-x-2">
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
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        const confirmed = window.confirm(`Delete assessment for ${assessment.company_name}?`);
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
          
          {/* Detailed Assessment View */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Assessment Details - {selectedAssessment?.company_name}
            </h2>
            
            {selectedAssessment ? (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Company</label>
                    <p className="mt-1 text-sm text-gray-900">{selectedAssessment.company_name}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Domain</label>
                    <p className="mt-1 text-sm text-gray-900">{selectedAssessment.domain || 'N/A'}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Risk Level</label>
                    <p className="mt-1 text-sm text-gray-900">{selectedAssessment.risk_assessment_data?.risk_level || 'N/A'}</p>
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Risk Categories</label>
                  <div className="space-y-2">
                    {Object.entries(selectedAssessment.risk_assessment_data?.risk_categories || {}).map(([key, category]) => (
                      <div key={key} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                        <span className="font-medium">{key.replace('_', ' ').toUpperCase()}</span>
                        <span className="text-sm text-gray-600">Score: {category.average_score?.toFixed(1) || 'N/A'}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-gray-600">No assessment selected.</p>
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
const App = () => {
  const [user, setUser] = useState(null);
  const [currentPage, setCurrentPage] = useState('dashboard');

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    setUser(null);
    setCurrentPage('dashboard');
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

  if (!user) {
    return <LoginPage onLogin={handleLogin} />;
  }

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <Header user={user} onLogout={handleLogout} />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar currentPage={currentPage} onPageChange={setCurrentPage} />
        <main className="flex-1 overflow-auto">
          {renderCurrentPage()}
        </main>
      </div>
    </div>
  );
};

export default App;