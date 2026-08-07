import { ChangePasswordForm } from '../components/ChangePasswordForm';
import { PageHeader } from '@/components/layout/PageHeader';

export function SettingsPage() {
  return (
    <div className="grid gap-6">
      <PageHeader
        title="Settings"
        description="Update your account security settings."
      />
      <section className="grid gap-3">
        <h2 className="text-lg font-medium">Change password</h2>
        <ChangePasswordForm />
      </section>
    </div>
  );
}
