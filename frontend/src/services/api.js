/**
 * API Service for making HTTP requests to the backend
 */
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refreshToken');
        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {}, {
          headers: {
            Authorization: `Bearer ${refreshToken}`,
          },
        });

        const { access_token } = response.data;
        localStorage.setItem('accessToken', access_token);

        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  verifyOTP: (data) => api.post('/auth/verify-otp', data),
  resendOTP: (data) => api.post('/auth/resend-otp', data),
  forgotPassword: (data) => api.post('/auth/forgot-password', data),
  resetPassword: (data) => api.post('/auth/reset-password', data),
  getCurrentUser: () => api.get('/auth/me'),
};

// Student API
export const studentAPI = {
  getProfile: () => api.get('/student/profile'),
  updateProfile: (data) => api.put('/student/profile', data),
  completeRegistration: () => api.post('/student/complete-registration'),
  getDashboard: () => api.get('/student/dashboard'),
};

// Document API
export const documentAPI = {
  upload: (formData) => api.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  list: () => api.get('/documents/list'),
  download: (id) => api.get(`/documents/${id}/download`, { responseType: 'blob' }),
  getPending: (page = 1) => api.get(`/documents/pending?page=${page}`),
  verify: (id, action, reason = '') => api.put(`/documents/${id}/verify`, { action, reason }),
};

// Payment API
export const paymentAPI = {
  createOrder: (data) => api.post('/payment/create-order', data),
  verify: (data) => api.post('/payment/verify', data),
  getHistory: () => api.get('/payment/history'),
  requestRefund: (id, reason) => api.post(`/payment/${id}/request-refund`, { reason }),
  processRefund: (id) => api.post(`/payment/${id}/process-refund`),
};

// Choice API
export const choiceAPI = {
  getEligibleColleges: () => api.get('/choices/eligible-colleges'),
  add: (data) => api.post('/choices/add', data),
  list: () => api.get('/choices/list'),
  remove: (id) => api.delete(`/choices/${id}/remove`),
  reorder: (data) => api.put('/choices/reorder', data),
  submit: () => api.post('/choices/submit'),
};

// Allotment API
export const allotmentAPI = {
  getMyAllotment: () => api.get('/allotment/my-allotment'),
  accept: (id, freeze) => api.post(`/allotment/${id}/accept`, { freeze }),
  reject: (id, reason) => api.post(`/allotment/${id}/reject`, { reason }),
  getRounds: () => api.get('/allotment/rounds'),
  getRoundDetails: (id) => api.get(`/allotment/round/${id}`),
  getStatistics: () => api.get('/allotment/statistics'),
};

// Admin API
export const adminAPI = {
  getDashboard: () => api.get('/admin/dashboard'),
  getStudents: (params) => api.get('/admin/students', { params }),
  generateReport: (params) => api.get('/admin/reports/applications', { params }),
  triggerAllotment: (data) => api.post('/admin/allotment/trigger', data),
  getColleges: () => api.get('/admin/colleges'),
  getCourses: () => api.get('/admin/courses'),
};

export default api;
