import { Cloud, MoreHorizontal } from 'lucide-react';
import { Link } from 'react-router-dom';

import { PATHS } from '@/app/routes/paths';
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
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { cn } from '@/lib/utils';
import { formatConnectionLabel } from '../utils/formatConnectionLabel';
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

export function ConnectionCard({
  connection,
  onDisconnect,
  onRename,
  onDisable,
  onEnable,
  onHealthCheck,
  isDisconnecting,
  isCheckingHealth,
  isEnabling,
}) {
  const title = formatConnectionLabel(connection, { includeEmail: false });
  const subtitle =
    connection.account_email &&
    connection.account_email.toLowerCase() !== title.toLowerCase()
      ? connection.account_email
      : connection.provider_label;

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
                {subtitle || connection.provider_label}
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
        {connection.status === 'active' ? (
          <Button
            size="sm"
            render={<Link to={PATHS.cloudFiles(connection.uuid)} />}
          >
            Browse files
          </Button>
        ) : null}
        <DropdownMenu>
          <DropdownMenuTrigger
            render={
              <Button
                variant="outline"
                size="icon-sm"
                aria-label={`More actions for ${title}`}
              />
            }
          >
            <MoreHorizontal />
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => onRename(connection)}>
              Rename
            </DropdownMenuItem>
            <DropdownMenuItem
              disabled={isCheckingHealth}
              onClick={() => onHealthCheck(connection.uuid)}
            >
              {isCheckingHealth ? 'Checking…' : 'Check health'}
            </DropdownMenuItem>
            {connection.status === 'active' ? (
              <DropdownMenuItem onClick={() => onDisable(connection)}>
                Disable
              </DropdownMenuItem>
            ) : null}
            {connection.status === 'disabled' ? (
              <DropdownMenuItem
                disabled={isEnabling}
                onClick={() => onEnable(connection.uuid)}
              >
                {isEnabling ? 'Enabling…' : 'Enable'}
              </DropdownMenuItem>
            ) : null}
            <DropdownMenuSeparator />
            <DropdownMenuItem
              variant="destructive"
              disabled={isDisconnecting}
              onClick={() => onDisconnect(connection.uuid)}
            >
              Disconnect
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
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
