import { useState, useEffect } from 'react';

// Service to handle API communication with health check
class ApiService {
  constructor() {
    this.backendUrl = import.meta.env.VITE_API_BASE_URL || '/api';
    this.isBackendHealthy = false;
    this.healthCheckPromise = null;
    this.lastHealthCheck = 0;
    this.healthCheckTTL = 5000; // 5 seconds TTL for health check cache
  }

  // Check if backend is available
  async checkBackendHealth(forceRefresh = false) {
    console.log('[DEBUG] Backend URL:', this.backendUrl);
    const healthUrl = `${this.backendUrl}/health`;
    console.log('[DEBUG] Fetching from:', healthUrl);

    const now = Date.now();
    const cacheExpired = now - this.lastHealthCheck > this.healthCheckTTL;

    // Return cached promise if it exists and cache hasn't expired (unless force refresh)
    if (this.healthCheckPromise && !cacheExpired && !forceRefresh) {
      console.log('[DEBUG] Using cached health check result');
      return this.healthCheckPromise;
    }

    // Clear old promise and create new one
    this.healthCheckPromise = new Promise(async (resolve) => {
      try {
        const response = await fetch(healthUrl, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        console.log('[DEBUG] Health check status:', response.status);
        if (response.ok) {
          const data = await response.json();
          console.log('[DEBUG] Health check succeeded:', data);
          this.isBackendHealthy = data.status === 'healthy';
          this.lastHealthCheck = Date.now();
          resolve(this.isBackendHealthy);
        } else {
          console.warn('Backend health check failed:', response.status);
          this.isBackendHealthy = false;
          this.lastHealthCheck = Date.now();
          resolve(false);
        }
      } catch (error) {
        console.error('[DEBUG] Health check FAILED:', error);
        this.isBackendHealthy = false;
        this.lastHealthCheck = Date.now();
        resolve(false);
      } finally {
        // Clear the promise after TTL so it can be retried
        setTimeout(() => {
          this.healthCheckPromise = null;
        }, this.healthCheckTTL);
      }
    });

    return this.healthCheckPromise;
  }

  // Generic API request method with error handling
  async request(endpoint, options = {}) {
    // CRITICAL FIX: Don't block requests based on cached health check
    // Instead, try the request and let it fail naturally if backend is down
    // This prevents false negatives from stale health check cache

    // ADD LOGGING: Frontend request logging
    console.log('[FRONTEND REQUEST]', options.method || 'GET', `${this.backendUrl}${endpoint}`, 'Data:', options.body);

    try {
      const response = await fetch(`${this.backendUrl}${endpoint}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      console.log('[FRONTEND RESPONSE]', response.status, response.statusText);

      if (!response.ok) {
        // Handle different error statuses appropriately
        if (response.status >= 500) {
          this.isBackendHealthy = false; // Mark as unhealthy if server error occurs
          this.healthCheckPromise = null; // Clear cache to force recheck
          throw new Error(`Server error: ${response.status}. Backend may be down.`);
        } else if (response.status >= 400) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.error || errorData.detail || `Request failed: ${response.status}`);
        } else {
          throw new Error(`Request failed: ${response.status}`);
        }
      }

      // On successful response, mark backend as healthy and update cache
      this.isBackendHealthy = true;
      this.lastHealthCheck = Date.now();

      const data = await response.json();
      console.log('[FRONTEND RESPONSE DATA]', data);
      return data;
    } catch (error) {
      if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
        this.isBackendHealthy = false; // Mark as unhealthy if network error occurs
        this.healthCheckPromise = null; // Clear cache to force recheck
        throw new Error('Connection failed. Please check if the backend server is running.');
      }
      throw error;
    }
  }
}

export const apiService = new ApiService();

// Custom hook to check backend availability with periodic retries
export const useBackendHealth = () => {
  const [isHealthy, setIsHealthy] = useState(null); // null = checking, boolean = result
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const checkHealth = async (forceRefresh = false) => {
      setLoading(true);
      try {
        const healthy = await apiService.checkBackendHealth(forceRefresh);
        setIsHealthy(healthy);
      } catch (error) {
        setIsHealthy(false);
      } finally {
        setLoading(false);
      }
    };

    // Initial health check
    checkHealth(true);

    // Set up periodic health checks every 30 seconds (reduced from 10s to minimize spam)
    const intervalId = setInterval(() => {
      checkHealth(true);
    }, 30000);

    // Cleanup interval on unmount
    return () => clearInterval(intervalId);
  }, []);

  return {
    isHealthy,
    loading,
    checkHealth: (forceRefresh = false) => apiService.checkBackendHealth(forceRefresh)
  };
};