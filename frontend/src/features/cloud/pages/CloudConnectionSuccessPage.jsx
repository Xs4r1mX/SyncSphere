import { CircleCheck } from 'lucide-react';
import { Link, useSearchParams } from 'react-router-dom';
import { useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';

import { PATHS } from '@/app/routes/paths';
import { buttonVariants } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { cloudQueryKeys } from '@/features/cloud/constants/queryKeys';
import { cn } from '@/lib/utils';

export function CloudConnectionSuccessPage() {
  const [searchParams] = useSearchParams();
  const queryClient = useQueryClient();
  const connectionUuid = searchParams.get('connection_uuid');

  useEffect(() => {
    queryClient.invalidateQueries({ queryKey: cloudQueryKeys.connections() });
  }, [queryClient]);

  return (
    <Card>
      <CardHeader className="justify-items-center text-center">
        <div className="mb-1 flex size-12 items-center justify-center rounded-full border border-border bg-emerald-500/10 text-emerald-500">
          <CircleCheck className="size-6" />
        </div>
        <CardTitle>Cloud account connected</CardTitle>
        <CardDescription>
          {connectionUuid
            ? 'Your cloud storage account was linked successfully and is ready to use.'
            : 'Your cloud storage account was linked successfully and is ready to use.'}
        </CardDescription>
      </CardHeader>
      <CardContent className="grid gap-3">
        <Link to={PATHS.CLOUD_STORAGES} className={cn(buttonVariants(), 'w-full')}>
          View connections
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
