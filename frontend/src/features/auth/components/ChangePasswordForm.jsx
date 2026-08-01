import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

import { FormField } from './FormField';
import { useChangePassword } from '../hooks/useChangePassword';
import { changePasswordSchema } from '../validation/changePasswordSchema';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';

export function ChangePasswordForm() {
  const changePassword = useChangePassword();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(changePasswordSchema),
    defaultValues: {
      old_password: '',
      new_password: '',
      confirm_password: '',
    },
  });

  const onSubmit = (values) => {
    changePassword.mutate(values);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="grid max-w-md gap-4">
      {changePassword.error ? (
        <Alert variant="destructive">
          <AlertDescription>{changePassword.error.message}</AlertDescription>
        </Alert>
      ) : null}

      <FormField
        id="old_password"
        label="Current password"
        type="password"
        autoComplete="current-password"
        error={
          errors.old_password?.message ||
          changePassword.error?.fieldErrors?.old_password
        }
        registration={register('old_password')}
      />

      <FormField
        id="new_password"
        label="New password"
        type="password"
        autoComplete="new-password"
        error={
          errors.new_password?.message ||
          changePassword.error?.fieldErrors?.new_password
        }
        registration={register('new_password')}
      />

      <FormField
        id="confirm_password"
        label="Confirm new password"
        type="password"
        autoComplete="new-password"
        error={errors.confirm_password?.message}
        registration={register('confirm_password')}
      />

      <Button type="submit" disabled={changePassword.isPending}>
        {changePassword.isPending ? 'Updating…' : 'Update password'}
      </Button>
    </form>
  );
}
