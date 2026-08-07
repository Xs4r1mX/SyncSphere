import { Link } from 'react-router-dom';
import {
  Activity,
  ArrowLeftRight,
  Cloud,
  HardDrive,
} from 'lucide-react';

import { PageHeader } from '@/components/layout/PageHeader';
import { PATHS } from '@/app/routes/paths';
import { useAuth } from '@/features/auth';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { mockRecentActivity } from '../data/mockRecentActivity';
import { statCards } from '../data/statCards';

export function DashboardPage() {
  const { user } = useAuth();

  return (
    <div className="grid gap-6">
      <PageHeader
        title={`Welcome${user?.first_name ? `, ${user.first_name}` : ''}`}
        description="Your cloud storage workspace overview."
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {statCards.map((stat) => {
          const Icon = stat.icon;

          return (
            <Card key={stat.label} size="sm">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.label}
                </CardTitle>
                <Icon className="size-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-semibold">{stat.value}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Quick actions</CardTitle>
            <CardDescription>
              Jump to common tasks across your workspace.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-2">
            <Button render={<Link to={PATHS.CLOUD_STORAGES} />} variant="secondary">
              <Cloud />
              Manage cloud storages
            </Button>
            <Button render={<Link to={PATHS.TRANSFER_HISTORY} />} variant="secondary">
              <ArrowLeftRight />
              View transfer history
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent activity</CardTitle>
            <CardDescription>
              Latest events from your connected services.
            </CardDescription>
          </CardHeader>
          <CardContent className="grid gap-3">
            {mockRecentActivity.map((entry) => {
              const Icon = entry.icon;

              return (
                <div
                  key={entry.id}
                  className="flex items-start gap-3 rounded-lg border border-border/60 bg-muted/20 p-3"
                >
                  <div className="flex size-8 shrink-0 items-center justify-center rounded-md bg-muted">
                    <Icon className="size-4 text-muted-foreground" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium">{entry.title}</p>
                    <p className="text-xs text-muted-foreground">{entry.timestamp}</p>
                  </div>
                </div>
              );
            })}
            <Button render={<Link to={PATHS.ACTIVITY} />} variant="ghost" className="justify-start px-0">
              <Activity />
              View all activity
            </Button>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Storage overview</CardTitle>
          <CardDescription>
            A snapshot of usage across connected providers.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex items-center gap-4 text-muted-foreground">
          <HardDrive className="size-8 shrink-0" />
          <p className="text-sm">
            Connect cloud storages to see usage breakdowns and quota details here.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
