// src/services/api.ts
import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  // timeout: 100000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证token等
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    const { response } = error;
    
    // 错误处理
    if (response) {
      // 服务器返回了错误响应
      console.error('API Error:', response.status, response.data);
      
      // 根据状态码处理特定错误
      switch (response.status) {
        case 401:
          // 未授权处理
          break;
        case 404:
          // 资源不存在处理
          break;
        case 500:
          // 服务器错误处理
          break;
        default:
          // 其他错误处理
          break;
      }
    } else {
      // 网络错误或请求被取消
      console.error('Network Error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

export default api;