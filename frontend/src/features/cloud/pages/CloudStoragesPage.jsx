import { Plus } from 'lucide-react';
import { toast } from 'sonner';

import { PageHeader } from '@/components/layout/PageHeader';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { ConnectionCard, ProviderCard } from '../components/ConnectionCard';
import { mockConnections, mockProviders } from '../data/mockConnections';

export function CloudStoragesPage() {
  const hasConnections = mockConnections.length > 0;

  return (
    <div className="grid gap-6">
      <PageHeader
        title="Cloud Storages"
        description="Manage your connected cloud accounts."
        action={
          <Button onClick={() => toast.info('Cloud connection will be available soon.')}>
            <Plus />
            Connect storage
          </Button>
        }
      />

      {hasConnections ? (
        <section className="grid gap-4 md:grid-cols-2">
          {mockConnections.map((connection) => (
            <ConnectionCard key={connection.id} connection={connection} />
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
            <Button onClick={() => toast.info('Cloud connection will be available soon.')}>
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
          {mockProviders.map((provider) => (
            <ProviderCard key={provider.id} provider={provider} />
          ))}
        </div>
      </section>
    </div>
  );
}
