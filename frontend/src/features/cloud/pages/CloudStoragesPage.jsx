import { Plus } from 'lucide-react';

import { PageHeader } from '@/components/layout/PageHeader';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { ConnectionCard, ProviderCard } from '../components/ConnectionCard';
import { cloudProviders } from '../constants/providers';
import { useCloudConnections } from '../hooks/useCloudConnections';
import { useConnectProvider } from '../hooks/useConnectProvider';
import { useUnlinkConnection } from '../hooks/useUnlinkConnection';

function ConnectionsSkeleton() {
  return (
    <section className="grid gap-4 md:grid-cols-2">
      {[0, 1].map((item) => (
        <Card key={item}>
          <CardHeader>
            <Skeleton className="h-5 w-40" />
            <Skeleton className="h-4 w-56" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-2 w-full" />
          </CardContent>
        </Card>
      ))}
    </section>
  );
}

export function CloudStoragesPage() {
  const connectionsQuery = useCloudConnections();
  const connectProvider = useConnectProvider();
  const unlinkConnection = useUnlinkConnection();

  const connections = connectionsQuery.data ?? [];
  const hasConnections = connections.length > 0;
  const connectingProviderId = connectProvider.isPending
    ? connectProvider.variables
    : null;

  return (
    <div className="grid gap-6">
      <PageHeader
        title="Cloud Storages"
        description="Manage your connected cloud accounts."
        action={
          <Button
            disabled={connectProvider.isPending}
            onClick={() => connectProvider.mutate('google_drive')}
          >
            <Plus />
            Connect storage
          </Button>
        }
      />

      {connectionsQuery.isError ? (
        <Alert variant="destructive">
          <AlertDescription>
            {connectionsQuery.error.message || 'Could not load cloud connections.'}
          </AlertDescription>
        </Alert>
      ) : null}

      {connectionsQuery.isLoading ? (
        <ConnectionsSkeleton />
      ) : hasConnections ? (
        <section className="grid gap-4 md:grid-cols-2">
          {connections.map((connection) => (
            <ConnectionCard
              key={connection.uuid}
              connection={connection}
              isDisconnecting={
                unlinkConnection.isPending &&
                unlinkConnection.variables === connection.uuid
              }
              onDisconnect={(uuid) => unlinkConnection.mutate(uuid)}
            />
          ))}
        </section>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>No connections yet</CardTitle>
            <CardDescription>
              Connect a cloud provider to start syncing and transferring files.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button
              disabled={connectProvider.isPending}
              onClick={() => connectProvider.mutate('google_drive')}
            >
              <Plus />
              Connect your first storage
            </Button>
          </CardContent>
        </Card>
      )}

      <section className="grid gap-4">
        <div className="grid gap-1">
          <h2 className="text-lg font-medium">Available providers</h2>
          <p className="text-sm text-muted-foreground">
            Choose a provider to link with your SyncSphere account.
          </p>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          {cloudProviders.map((provider) => (
            <ProviderCard
              key={provider.id}
              provider={provider}
              isConnecting={connectingProviderId === provider.id}
              onConnect={(providerId) => connectProvider.mutate(providerId)}
            />
          ))}
        </div>
      </section>
    </div>
  );
}
