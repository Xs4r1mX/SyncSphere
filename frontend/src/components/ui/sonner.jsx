import { useTheme } from 'next-themes';
import { Toaster as Sonner } from 'sonner';
import {
  CircleCheckIcon,
  InfoIcon,
  TriangleAlertIcon,
  OctagonXIcon,
  Loader2Icon,
} from 'lucide-react';

const Toaster = ({ ...props }) => {
  const { theme = 'system' } = useTheme();

  return (
    <Sonner
      theme={theme}
      className="toaster group"
      icons={{
        success: <CircleCheckIcon className="size-4 text-emerald-400" />,
        info: <InfoIcon className="size-4 text-sky-400" />,
        warning: <TriangleAlertIcon className="size-4 text-amber-400" />,
        error: <OctagonXIcon className="size-4 text-destructive" />,
        loading: <Loader2Icon className="size-4 animate-spin text-muted-foreground" />,
      }}
      style={{
        '--normal-bg': 'var(--card)',
        '--normal-text': 'var(--card-foreground)',
        '--normal-border': 'var(--border)',
        '--border-radius': 'var(--radius-xl)',
        // Keep the close button inside the toast instead of the default
        // overhanging top-left placement.
        '--toast-close-button-start': 'unset',
        '--toast-close-button-end': '0',
        '--toast-close-button-transform': 'translate(-10px, 10px)',
      }}
      toastOptions={{
        classNames: {
          toast: 'cn-toast group toast',
          actionButton: 'bg-primary text-primary-foreground hover:bg-primary/90',
          cancelButton: 'bg-muted text-muted-foreground hover:bg-muted/80',
        },
      }}
      {...props}
    />
  );
};

export { Toaster };
