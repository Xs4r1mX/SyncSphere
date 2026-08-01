import { ReduxProvider } from './ReduxProvider';
import { QueryProvider } from './QueryProvider';
import { ThemeProvider } from './ThemeProvider';
import { ToastProvider } from './ToastProvider';

export function AppProviders({ children }) {
  return (
    <ReduxProvider>
      <QueryProvider>
        <ThemeProvider>
          {children}
          <ToastProvider />
        </ThemeProvider>
      </QueryProvider>
    </ReduxProvider>
  );
}