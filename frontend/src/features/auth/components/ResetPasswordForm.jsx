import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link } from 'react-router-dom';

import { FormField } from './FormField';
import { useResetPassword } from '../hooks/useResetPassword';
import { resetPasswordSchema } from '../validation/resetPasswordSchema';
import { PATHS } from '@/app/routes/paths';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';

export function ResetPasswordForm({ token }) {
  const resetPassword = useResetPassword();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: {
      new_password: '',
      confirm_password: '',
    },
  });

  const onSubmit = (values) => {
    resetPassword.mutate({
      token,
      new_password: values.new_password,
      confirm_password: values.confirm_password,
    });
  };

  if (!token) {
    return (
      <div className="grid gap-4">
        <Alert variant="destructive">
          <AlertDescription>
            This reset link is invalid or missing a token.
          </AlertDescription>
        </Alert>
        <Link
          to={PATHS.FORGOT_PASSWORD}
          className="text-center text-sm underline-offset-4 hover:underline"
        >
          Request a new reset link
        </Link>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="grid gap-4">
      {resetPassword.error ? (
        <Alert variant="destructive">
          <AlertDescription>{resetPassword.error.message}</AlertDescription>
        </Alert>
      ) : null}

      <FormField
        id="new_password"
        label="New password"
        type="password"
        autoComplete="new-password"
        error={
          errors.new_password?.message ||
          resetPassword.error?.fieldErrors?.new_password
        }
        registration={register('new_password')}
      />

      <FormField
        id="confirm_password"
        label="Confirm password"
        type="password"
        autoComplete="new-password"
        error={
          errors.confirm_password?.message ||
          resetPassword.error?.fieldErrors?.confirm_password
        }
        registration={register('confirm_password')}
      />

      <Button type="submit" disabled={resetPassword.isPending}>
        {resetPassword.isPending ? 'Resetting…' : 'Reset password'}
      </Button>
    </form>
  );
}
