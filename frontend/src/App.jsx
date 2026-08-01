import { RouterProvider } from 'react-router-dom';

import { router } from '@/app/routes/router';
import { useAuthBootstrap } from '@/features/auth';

export default function App() {
  useAuthBootstrap();

  return <RouterProvider router={router} />;
}
