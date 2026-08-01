import React from 'react';
import ReactDOM from 'react-dom/client';

import App from './App';

import './index.css';
import './styles/globals.css';

import { AppProviders } from '@/app/providers/AppProviders';
import { AppRouter } from '@/app/routes/AppRouter';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AppProviders>
      <AppRouter>
        <App />
      </AppRouter>
    </AppProviders>
  </React.StrictMode>
);