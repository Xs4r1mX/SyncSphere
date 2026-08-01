import axios from 'axios';
import env from '@/app/config/env';

const api = axios.create({
  baseURL: env.apiBaseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;