// frontend/src/components/ConnectionStatus.js

import React, { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle, RefreshCw } from 'lucide-react';
import apiService from '../services/api';

const ConnectionStatus = () => {
  const [connectionStatus, setConnectionStatus] = useState('checking');
  const [backendInfo, setBackendInfo] = useState(null);
  const [error, setError] = useState(null);
  const [isChecking, setIsChecking] = useState(false);

  const checkConnection = async () => {
    setIsChecking(true);
    setError(null);
    
    try {
      console.log('Checking backend connection...');
      const health = await apiService.checkBackendHealth();
      setConnectionStatus('connected');
      setBackendInfo(health);
      console.log('Connection successful:', health);
    } catch (err) {
      console.error('Connection failed:', err);
      setConnectionStatus('failed');
      setError(err.message);
      setBackendInfo(null);
    } finally {
      setIsChecking(false);
    }
  };

  useEffect(() => {
    checkConnection();
    // Check connection every 30 seconds
    const interval = setInterval(checkConnection, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return 'text-green-600 bg-green-50';
      case 'failed': return 'text-red-600 bg-red-50';
      default: return 'text-yellow-600 bg-yellow-50';
    }
  };

  const getStatusIcon = () => {
    if (isChecking) return <RefreshCw className="w-4 h-4 animate-spin" />;
    switch (connectionStatus) {
      case 'connected': return <CheckCircle className="w-4 h-4" />;
      case 'failed': return <AlertCircle className="w-4 h-4" />;
      default: return <RefreshCw className="w-4 h-4" />;
    }
  };

  const getStatusText = () => {
    switch (connectionStatus) {
      case 'connected': return 'Backend Connected';
      case 'failed': return 'Backend Connection Failed';
      default: return 'Checking Connection...';
    }
  };

  return (
    <div className={`flex items-center justify-between p-3 rounded-lg border ${getStatusColor()}`}>
      <div className="flex items-center space-x-2">
        {getStatusIcon()}
        <span className="font-medium">{getStatusText()}</span>
      </div>
      
      <div className="flex items-center space-x-2">
        {backendInfo && (
          <span className="text-sm">
            v{backendInfo.version} | {backendInfo.services?.database}
          </span>
        )}
        <button
          onClick={checkConnection}
          disabled={isChecking}
          className="px-3 py-1 text-sm bg-white border rounded hover:bg-gray-50 disabled:opacity-50"
        >
          {isChecking ? 'Checking...' : 'Retry'}
        </button>
      </div>

      {error && (
        <div className="mt-2 p-2 bg-red-100 border border-red-200 rounded text-sm text-red-700">
          <strong>Error:</strong> {error}
          <br />
          <strong>Backend URL:</strong> {apiService.baseURL}
        </div>
      )}

      {connectionStatus === 'failed' && (
        <div className="mt-2 p-2 bg-yellow-100 border border-yellow-200 rounded text-sm text-yellow-700">
          <strong>Troubleshooting:</strong>
          <ul className="list-disc list-inside mt-1">
            <li>Check if backend is running locally on port 8000</li>
            <li>Verify Render deployment is active</li>
            <li>Check browser console for detailed errors</li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default ConnectionStatus;