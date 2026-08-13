import { useMemo, useState } from 'react';
import { Search } from 'lucide-react';

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
import { Input } from '@/components/ui/input';
import { SelectField } from '@/components/ui/select';
import { Skeleton } from '@/components/ui/skeleton';
import { ActivityDetailDialog } from '../components/ActivityDetailDialog';
import { ActivityTimelineItem } from '../components/ActivityTimelineItem';
import { RESOURCE_TYPE_FILTER_OPTIONS } from '../constants/actions';
import { useActivityFeed } from '../hooks/useActivity';
import {
  formatActivityTitle,
  groupActivityByDay,
} from '../utils/formatActivity';

function ActivitySkeleton() {
  return (
    <Card>
      <CardContent className="grid gap-8 p-6">
        {[0, 1, 2].map((row) => (
          <div key={row} className="grid grid-cols-[4.5rem_1.75rem_1fr] gap-x-3">
            <Skeleton className="mt-2 ml-auto h-3 w-12" />
            <Skeleton className="size-9 rounded-full" />
            <div className="grid gap-3 pt-1">
              <Skeleton className="h-4 w-40" />
              <Skeleton className="h-16 w-full max-w-xl" />
              <Skeleton className="h-3 w-48" />
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

export function ActivityPage() {
  const [resourceType, setResourceType] = useState('all');
  const [search, setSearch] = useState('');
  const [selectedUuid, setSelectedUuid] = useState(null);

  const activityQuery = useActivityFeed({
    resource_type: resourceType,
    limit: 50,
  });

  const items =
    activityQuery.data?.pages.flatMap((page) => page.items) ?? [];

  const filteredItems = useMemo(() => {
    const query = search.trim().toLowerCase();

    if (!query) {
      return items;
    }

    return items.filter((entry) => {
      const title = formatActivityTitle(entry);
      const name = entry.resource_name ?? '';
      const provider = entry.provider ?? '';
      const type = entry.resource_type ?? '';

      return (
        title.toLowerCase().includes(query) ||
        name.toLowerCase().includes(query) ||
        provider.toLowerCase().includes(query) ||
        type.toLowerCase().includes(query)
      );
    });
  }, [items, search]);

  const dayGroups = useMemo(
    () => groupActivityByDay(filteredItems),
    [filteredItems],
  );

  return (
    <div className="grid gap-6">
      <PageHeader
        title="Activity"
        description="Track recent events across your SyncSphere workspace."
      />

      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
          <CardDescription>
            Search by name or filter by resource type.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-3 sm:flex-row">
          <div className="relative flex-1">
            <Search className="absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              className="pl-9"
              placeholder="Search activity..."
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              aria-label="Search activity"
            />
          </div>
          <SelectField
            className="sm:w-48"
            value={resourceType}
            onValueChange={setResourceType}
            aria-label="Filter by resource type"
            options={RESOURCE_TYPE_FILTER_OPTIONS}
          />
        </CardContent>
      </Card>

      {activityQuery.isError ? (
        <Alert variant="destructive">
          <AlertDescription>
            {activityQuery.error.message || 'Could not load activity.'}
          </AlertDescription>
        </Alert>
      ) : null}

      {activityQuery.isLoading ? (
        <ActivitySkeleton />
      ) : filteredItems.length === 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>No activity yet</CardTitle>
            <CardDescription>
              Connect a cloud storage, manage files, or start a transfer to see
              events here.
            </CardDescription>
          </CardHeader>
        </Card>
      ) : (
        <Card className="overflow-hidden">
          <CardContent className="grid gap-8 p-5 sm:p-6">
            {dayGroups.map((group) => (
              <section key={group.key} className="grid gap-6">
                <div className="flex items-center gap-3">
                  <h2 className="shrink-0 text-[11px] font-medium tracking-[0.14em] text-muted-foreground uppercase">
                    {group.label}
                  </h2>
                  <div className="h-px flex-1 bg-border" />
                </div>

                <div>
                  {group.items.map((entry, index) => (
                    <ActivityTimelineItem
                      key={entry.uuid}
                      entry={entry}
                      isLast={index === group.items.length - 1}
                      onSelect={(item) => setSelectedUuid(item.uuid)}
                    />
                  ))}
                </div>
              </section>
            ))}
          </CardContent>

          {activityQuery.hasNextPage ? (
            <div className="flex justify-center border-t border-border p-4">
              <Button
                variant="outline"
                disabled={activityQuery.isFetchingNextPage}
                onClick={() => activityQuery.fetchNextPage()}
              >
                {activityQuery.isFetchingNextPage ? 'Loading…' : 'Load more'}
              </Button>
            </div>
          ) : null}
        </Card>
      )}

      <ActivityDetailDialog
        open={Boolean(selectedUuid)}
        onOpenChange={(open) => {
          if (!open) {
            setSelectedUuid(null);
          }
        }}
        activityUuid={selectedUuid}
      />
    </div>
  );
}
