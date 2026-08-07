import { createBrowserRouter } from 'react-router-dom';

import { PATHS } from './paths';
import { ProtectedRoute } from './ProtectedRoute';
import { PublicRoute } from './PublicRoute';
import { HomeRedirect } from './HomeRedirect';
import { AuthLayout } from '@/layouts/AuthLayout';
import { DashboardLayout } from '@/layouts/DashboardLayout';
import { ActivityPage } from '@/features/activity';
import { CloudStoragesPage } from '@/features/cloud';
import { DashboardPage } from '@/features/dashboard';
import { TransferHistoryPage } from '@/features/transfers';
import {
  ForgotPasswordPage,
  LoginPage,
  RegisterPage,
  ResetPasswordPage,
  SettingsPage,
  VerifyEmailPage,
} from '@/features/auth';

export const router = createBrowserRouter([
  {
    path: PATHS.HOME,
    element: <HomeRedirect />,
  },
  {
    element: <PublicRoute />,
    children: [
      {
        element: <AuthLayout />,
        children: [
          { path: PATHS.LOGIN, element: <LoginPage /> },
          { path: PATHS.REGISTER, element: <RegisterPage /> },
          { path: PATHS.FORGOT_PASSWORD, element: <ForgotPasswordPage /> },
          { path: PATHS.RESET_PASSWORD, element: <ResetPasswordPage /> },
          { path: PATHS.VERIFY_EMAIL, element: <VerifyEmailPage /> },
        ],
      },
    ],
  },
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <DashboardLayout />,
        children: [
          { path: PATHS.DASHBOARD, element: <DashboardPage /> },
          { path: PATHS.CLOUD_STORAGES, element: <CloudStoragesPage /> },
          { path: PATHS.TRANSFER_HISTORY, element: <TransferHistoryPage /> },
          { path: PATHS.ACTIVITY, element: <ActivityPage /> },
          { path: PATHS.SETTINGS, element: <SettingsPage /> },
        ],
      },
    ],
  },
]);
