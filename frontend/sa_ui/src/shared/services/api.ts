// src/services/api.ts
import axios from 'axios';

// Create axios instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // You can add authentication tokens here
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    const { response } = error;
    
    // Error handling
    if (response) {
      // Server returned an error response
      console.error('API Error:', response.status, response.data);
      
      // Handle specific error codes
      switch (response.status) {
        case 401:
          // Unauthorized handling
          break;
        case 404:
          // Resource not found handling
          break;
        case 500:
          // Server error handling
          break;
        default:
          // Other error handling
          break;
      }
    } else {
      // Network error or request canceled
      console.error('Network Error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

// Enable mock mode for development
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true' || true;

export { USE_MOCK };
export default api;