import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link } from 'react-router-dom';

import { FormField } from './FormField';
import { useForgotPassword } from '../hooks/useForgotPassword';
import { forgotPasswordSchema } from '../validation/forgotPasswordSchema';
import { PATHS } from '@/app/routes/paths';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';

export function ForgotPasswordForm() {
  const forgotPassword = useForgotPassword();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: {
      email: '',
    },
  });

  const onSubmit = (values) => {
    forgotPassword.mutate(values);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="grid gap-4">
      {forgotPassword.error ? (
        <Alert variant="destructive">
          <AlertDescription>{forgotPassword.error.message}</AlertDescription>
        </Alert>
      ) : null}

      {forgotPassword.isSuccess ? (
        <Alert>
          <AlertDescription>
            A password reset link has been sent if that email is registered.
          </AlertDescription>
        </Alert>
      ) : null}

      <FormField
        id="email"
        label="Email"
        type="email"
        autoComplete="email"
        error={
          errors.email?.message || forgotPassword.error?.fieldErrors?.email
        }
        registration={register('email')}
      />

      <Button type="submit" disabled={forgotPassword.isPending}>
        {forgotPassword.isPending ? 'Sending…' : 'Send reset link'}
      </Button>

      <p className="text-center text-sm text-muted-foreground">
        <Link to={PATHS.LOGIN} className="underline-offset-4 hover:underline">
          Back to sign in
        </Link>
      </p>
    </form>
  );
}
