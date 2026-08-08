import { Cloud } from 'lucide-react';

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
import {
  formatQuotaLabel,
  getQuotaPercentage,
} from '../utils/formatQuota';

function getStatusVariant(status) {
  switch (status) {
    case 'active':
      return 'secondary';
    case 'error':
    case 'expired':
      return 'destructive';
    case 'disabled':
    case 'pending':
      return 'outline';
    default:
      return 'outline';
  }
}

function QuotaBar({ connection }) {
  const percentage = getQuotaPercentage(
    connection.quota_used_bytes,
    connection.quota_total_bytes,
  );
  const hasQuota =
    connection.quota_used_bytes != null || connection.quota_total_bytes != null;

  if (!hasQuota) {
    return (
      <p className="text-xs text-muted-foreground">Storage quota unavailable</p>
    );
  }

  return (
    <div className="grid gap-1.5">
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span>Storage used</span>
        <span>
          {formatQuotaLabel(
            connection.quota_used_bytes,
            connection.quota_total_bytes,
          )}
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

export function ConnectionCard({ connection, onDisconnect, isDisconnecting }) {
  const title = connection.display_name || connection.provider_label;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-lg bg-muted">
              <Cloud className="size-5 text-muted-foreground" />
            </div>
            <div>
              <CardTitle>{title}</CardTitle>
              <CardDescription>
                {connection.account_email || connection.provider_label}
              </CardDescription>
            </div>
          </div>
          <Badge variant={getStatusVariant(connection.status)}>
            {connection.status_label}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <QuotaBar connection={connection} />
      </CardContent>
      <CardFooter className="gap-2">
        <Button
          variant="ghost"
          size="sm"
          disabled={isDisconnecting}
          onClick={() => onDisconnect(connection.uuid)}
        >
          Disconnect
        </Button>
      </CardFooter>
    </Card>
  );
}

export function ProviderCard({ provider, onConnect, isConnecting }) {
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
          disabled={!provider.available || isConnecting}
          onClick={() => onConnect(provider.id)}
        >
          {isConnecting ? 'Connecting…' : 'Connect'}
        </Button>
      </CardFooter>
    </Card>
  );
}
