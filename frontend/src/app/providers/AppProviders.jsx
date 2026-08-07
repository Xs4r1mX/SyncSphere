import { TooltipProvider } from '@/components/ui/tooltip';

import { ReduxProvider } from './ReduxProvider';
import { QueryProvider } from './QueryProvider';
import { ThemeProvider } from './ThemeProvider';
import { ToastProvider } from './ToastProvider';

export function AppProviders({ children }) {
  return (
    <ReduxProvider>
      <QueryProvider>
        <ThemeProvider>
          <TooltipProvider>
            {children}
            <ToastProvider />
          </TooltipProvider>
        </ThemeProvider>
      </QueryProvider>
    </ReduxProvider>
  );
}