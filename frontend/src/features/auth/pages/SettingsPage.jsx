import { ChangePasswordForm } from '../components/ChangePasswordForm';

export function SettingsPage() {
  return (
    <div className="grid gap-6">
      <div className="grid gap-2">
        <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">
          Update your account security settings.
        </p>
      </div>
      <section className="grid gap-3">
        <h2 className="text-lg font-medium">Change password</h2>
        <ChangePasswordForm />
      </section>
    </div>
  );
}
