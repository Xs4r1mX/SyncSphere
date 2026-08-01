import { BrowserRouter } from 'react-router-dom';

export function AppRouter({ children }) {
  return <BrowserRouter>{children}</BrowserRouter>;
}