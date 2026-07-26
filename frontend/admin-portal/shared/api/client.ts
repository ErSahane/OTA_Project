import axios from 'axios';

/**
 * Centralised Axios instance for the Admin Portal.
 * All API calls go through this client so that we can set a base URL,
 * default timeout, and attach interceptors for error handling in one place.
 */
export const apiClient = axios.create({
  baseURL: '/api',
  timeout: 10000,
});
