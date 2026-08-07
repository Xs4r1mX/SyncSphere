import { PageHeader } from '@/components/layout/PageHeader';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { mockActivityEntries } from '../data/mockActivity';

export function ActivityPage() {
  return (
    <div className="grid gap-6">
      <PageHeader
        title="Activity"
        description="Track recent events across your SyncSphere workspace."
      />

      <Card>
        <CardHeader>
          <CardTitle>Recent events</CardTitle>
          <CardDescription>
            A timeline of connections, transfers, and account updates.
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-0">
          {mockActivityEntries.map((entry, index) => {
            const Icon = entry.icon;
            const isLast = index === mockActivityEntries.length - 1;

            return (
              <div key={entry.id} className="flex gap-4">
                <div className="flex flex-col items-center">
                  <div className="flex size-9 shrink-0 items-center justify-center rounded-full bg-muted">
                    <Icon className="size-4 text-muted-foreground" />
                  </div>
                  {!isLast ? (
                    <div className="my-1 w-px flex-1 bg-border" />
                  ) : null}
                </div>
                <div className={isLast ? 'pb-0' : 'pb-6'}>
                  <p className="text-sm font-medium">{entry.title}</p>
                  <p className="mt-0.5 text-sm text-muted-foreground">
                    {entry.description}
                  </p>
                  <p className="mt-1 text-xs text-muted-foreground">{entry.timestamp}</p>
                </div>
              </div>
            );
          })}
        </CardContent>
      </Card>
    </div>
  );
}
