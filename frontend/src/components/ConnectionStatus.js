// frontend/src/components/ConnectionStatus.js - Enhanced for Render free tier

import React, { useState, useEffect } from 'react';
import apiService from '../services/api';

const ConnectionStatus = () => {
  const [connectionStatus, setConnectionStatus] = useState('checking');
  const [backendInfo, setBackendInfo] = useState(null);
  const [error, setError] = useState(null);
  const [isChecking, setIsChecking] = useState(false);
  const [isWakingUp, setIsWakingUp] = useState(false);

  const checkConnection = async () => {
    setIsChecking(true);
    setError(null);
    
    try {
      console.log('Checking backend connection...');
      const health = await apiService.checkBackendHealth();
      setConnectionStatus('connected');
      setBackendInfo(health);
      setIsWakingUp(false);
      console.log('Connection successful:', health);
    } catch (err) {
      console.error('Connection failed:', err);
      setConnectionStatus('failed');
      setError(err.message);
      setBackendInfo(null);
      
      // Check if this might be a "cold start" issue
      if (err.message.includes('502') || err.message.includes('Bad Gateway') || err.message.includes('timeout')) {
        console.log('Detected possible cold start - backend may be waking up');
      }
    } finally {
      setIsChecking(false);
    }
  };

  const wakeUpBackend = async () => {
    setIsWakingUp(true);
    setError(null);
    
    try {
      console.log('Attempting to wake up backend (this may take 50+ seconds on free tier)...');
      
      // Try multiple times with longer timeouts
      for (let attempt = 1; attempt <= 3; attempt++) {
        try {
          console.log(`Wake-up attempt ${attempt}/3...`);
          
          const response = await fetch(`${apiService.baseURL}/health`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
            signal: AbortSignal.timeout(60000) // 60 second timeout for wake-up
          });
          
          if (response.ok) {
            const health = await response.json();
            setConnectionStatus('connected');
            setBackendInfo(health);
            setIsWakingUp(false);
            console.log('Backend successfully woken up!');
            return;
          }
        } catch (attemptError) {
          console.log(`Wake-up attempt ${attempt} failed:`, attemptError.message);
          if (attempt < 3) {
            console.log('Waiting 10 seconds before next attempt...');
            await new Promise(resolve => setTimeout(resolve, 10000));
          }
        }
      }
      
      // If all attempts failed
      setConnectionStatus('failed');
      setError('Failed to wake up backend after 3 attempts. Backend may need manual deployment.');
      
    } catch (error) {
      console.error('Wake-up process failed:', error);
      setConnectionStatus('failed');
      setError(error.message);
    } finally {
      setIsWakingUp(false);
    }
  };

  useEffect(() => {
    checkConnection();
    // Check connection every 30 seconds
    const interval = setInterval(checkConnection, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusStyle = () => {
    if (isWakingUp) {
      return {
        backgroundColor: '#fef3c7',
        color: '#92400e',
        borderColor: '#fbbf24'
      };
    }
    
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
    if (isWakingUp) return '🔄 Waking up backend (may take 60+ seconds)...';
    
    switch (connectionStatus) {
      case 'connected': return '✅ Backend Connected';
      case 'failed': return '❌ Backend Connection Failed';
      default: return '🔄 Checking Connection...';
    }
  };

  const showWakeUpButton = connectionStatus === 'failed' && 
    (error?.includes('502') || error?.includes('Bad Gateway') || error?.includes('timeout'));

  return (
    <div style={{
      ...getStatusStyle(),
      padding: '12px',
      borderRadius: '8px',
      border: '1px solid',
      marginBottom: '16px',
      position: 'relative'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
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
        
        <div style={{ display: 'flex', gap: '8px' }}>
          {showWakeUpButton && (
            <button
              onClick={wakeUpBackend}
              disabled={isWakingUp}
              style={{
                padding: '4px 12px',
                fontSize: '12px',
                backgroundColor: '#fbbf24',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: isWakingUp ? 'not-allowed' : 'pointer',
                opacity: isWakingUp ? 0.5 : 1
              }}
            >
              {isWakingUp ? 'Waking Up...' : 'Wake Up Backend'}
            </button>
          )}
          
          <button
            onClick={checkConnection}
            disabled={isChecking || isWakingUp}
            style={{
              padding: '4px 12px',
              fontSize: '12px',
              backgroundColor: 'white',
              border: '1px solid #d1d5db',
              borderRadius: '4px',
              cursor: (isChecking || isWakingUp) ? 'not-allowed' : 'pointer',
              opacity: (isChecking || isWakingUp) ? 0.5 : 1
            }}
          >
            {isChecking ? 'Checking...' : 'Retry'}
          </button>
        </div>
      </div>

      {error && (
        <div style={{
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
          {showWakeUpButton && (
            <>
              <br />
              <strong>💡 Tip:</strong> This looks like a "cold start" - your backend is sleeping. Click "Wake Up Backend" above.
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default ConnectionStatus;