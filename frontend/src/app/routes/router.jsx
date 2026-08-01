import { createBrowserRouter } from 'react-router-dom';

import { PATHS } from './paths';
import { ProtectedRoute } from './ProtectedRoute';
import { PublicRoute } from './PublicRoute';
import { HomeRedirect } from './HomeRedirect';
import { AuthLayout } from '@/layouts/AuthLayout';
import { DashboardLayout } from '@/layouts/DashboardLayout';
import {
  DashboardPage,
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
          { path: PATHS.SETTINGS, element: <SettingsPage /> },
        ],
      },
    ],
  },
]);
