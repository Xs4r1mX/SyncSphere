import { useAuth } from '../hooks/useAuth';

export function DashboardPage() {
  const { user } = useAuth();

  return (
    <div className="grid gap-2">
      <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
      <p className="text-muted-foreground">
        Welcome{user?.first_name ? `, ${user.first_name}` : ''}. Your cloud
        storage workspace will live here.
      </p>
    </div>
  );
}
