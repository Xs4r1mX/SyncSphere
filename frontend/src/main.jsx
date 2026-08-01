import React from 'react';
import ReactDOM from 'react-dom/client';

import App from './App';
import './index.css';
import '@/services/api/interceptors';

import { AppProviders } from '@/app/providers/AppProviders';
import env from '@/app/config/env';

document.title = env.appName;

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AppProviders>
      <App />
    </AppProviders>
  </React.StrictMode>
);
