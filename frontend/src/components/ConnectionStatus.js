// frontend/src/components/ConnectionStatus.js - Simple version with no external dependencies

import React, { useState, useEffect } from 'react';
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

  const getStatusStyle = () => {
    switch (connectionStatus) {
      case 'connected': 
        return {
          backgroundColor: '#f0f9ff',
          color: '#065f46',
          borderColor: '#10b981'
        };
      case 'failed': 
        return {
          backgroundColor: '#fef2f2',
          color: '#991b1b',
          borderColor: '#ef4444'
        };
      default: 
        return {
          backgroundColor: '#fffbeb',
          color: '#92400e',
          borderColor: '#f59e0b'
        };
    }
  };

  const getStatusText = () => {
    switch (connectionStatus) {
      case 'connected': return '✅ Backend Connected';
      case 'failed': return '❌ Backend Connection Failed';
      default: return '🔄 Checking Connection...';
    }
  };

  return (
    <div style={{
      ...getStatusStyle(),
      padding: '12px',
      borderRadius: '8px',
      border: '1px solid',
      marginBottom: '16px',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span style={{ fontWeight: '500' }}>
          {getStatusText()}
        </span>
        {backendInfo && (
          <span style={{ fontSize: '12px', opacity: 0.8 }}>
            v{backendInfo.version}
          </span>
        )}
      </div>
      
      <button
        onClick={checkConnection}
        disabled={isChecking}
        style={{
          padding: '4px 12px',
          fontSize: '12px',
          backgroundColor: 'white',
          border: '1px solid #d1d5db',
          borderRadius: '4px',
          cursor: isChecking ? 'not-allowed' : 'pointer',
          opacity: isChecking ? 0.5 : 1
        }}
      >
        {isChecking ? 'Checking...' : 'Retry'}
      </button>

      {error && (
        <div style={{
          position: 'absolute',
          top: '100%',
          left: 0,
          right: 0,
          marginTop: '8px',
          padding: '8px',
          backgroundColor: '#fef2f2',
          border: '1px solid #fecaca',
          borderRadius: '4px',
          fontSize: '12px',
          color: '#991b1b'
        }}>
          <strong>Error:</strong> {error}
          <br />
          <strong>Backend URL:</strong> {apiService.baseURL}
        </div>
      )}
    </div>
  );
};

export default ConnectionStatus;