import { CircleX } from 'lucide-react';
import { Link, useSearchParams } from 'react-router-dom';

import { PATHS } from '@/app/routes/paths';
import { buttonVariants } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { getOAuthErrorMessage } from '@/features/cloud/utils/oauthErrors';
import { cn } from '@/lib/utils';

export function CloudConnectionErrorPage() {
  const [searchParams] = useSearchParams();
  const errorCode = searchParams.get('error');
  const message = getOAuthErrorMessage(errorCode);

  return (
    <Card>
      <CardHeader className="justify-items-center text-center">
        <div className="mb-1 flex size-12 items-center justify-center rounded-full border border-border bg-destructive/10 text-destructive">
          <CircleX className="size-6" />
        </div>
        <CardTitle>Connection failed</CardTitle>
        <CardDescription>{message}</CardDescription>
      </CardHeader>
      <CardContent className="grid gap-3">
        <Link to={PATHS.CLOUD_STORAGES} className={cn(buttonVariants(), 'w-full')}>
          Try again
        </Link>
        <Link
          to={PATHS.DASHBOARD}
          className={cn(buttonVariants({ variant: 'outline' }), 'w-full')}
        >
          Back to dashboard
        </Link>
      </CardContent>
    </Card>
  );
}
