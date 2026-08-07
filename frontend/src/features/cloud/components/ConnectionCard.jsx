import { Cloud } from 'lucide-react';
import { toast } from 'sonner';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { cn } from '@/lib/utils';

function QuotaBar({ used, total }) {
  const percentage = Math.min(Math.round((used / total) * 100), 100);

  return (
    <div className="grid gap-1.5">
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span>Storage used</span>
        <span>
          {used} GB / {total} GB
        </span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-muted">
        <div
          className="h-full rounded-full bg-primary transition-all"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

export function ConnectionCard({ connection }) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-lg bg-muted">
              <Cloud className="size-5 text-muted-foreground" />
            </div>
            <div>
              <CardTitle>{connection.provider}</CardTitle>
              <CardDescription>{connection.email}</CardDescription>
            </div>
          </div>
          <Badge variant="secondary">{connection.status}</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <QuotaBar used={connection.quotaUsed} total={connection.quotaTotal} />
      </CardContent>
      <CardFooter className="gap-2">
        <Button variant="outline" size="sm" onClick={() => toast.info('Coming soon')}>
          Manage
        </Button>
        <Button variant="ghost" size="sm" onClick={() => toast.info('Coming soon')}>
          Disconnect
        </Button>
      </CardFooter>
    </Card>
  );
}

export function ProviderCard({ provider }) {
  return (
    <Card className={cn(!provider.available && 'opacity-80')}>
      <CardHeader>
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="text-base">{provider.name}</CardTitle>
          {!provider.available ? (
            <Badge variant="outline">Coming soon</Badge>
          ) : null}
        </div>
        <CardDescription>{provider.description}</CardDescription>
      </CardHeader>
      <CardFooter>
        <Button
          size="sm"
          disabled={!provider.available}
          onClick={() => toast.info('Cloud connection will be available soon.')}
        >
          Connect
        </Button>
      </CardFooter>
    </Card>
  );
}
