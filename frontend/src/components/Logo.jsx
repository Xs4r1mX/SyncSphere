import { cn } from '@/lib/utils';
import env from '@/app/config/env';

const LOGO_SRC = '/syncSphere.png';

const sizes = {
  sm: 'h-8',
  md: 'h-12',
  lg: 'h-16',
};

export function Logo({ size = 'md', className, ...props }) {
  return (
    <img
      src={LOGO_SRC}
      alt={env.appName}
      className={cn('w-auto object-contain', sizes[size], className)}
      {...props}
    />
  );
}
