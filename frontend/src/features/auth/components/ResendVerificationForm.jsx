import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

import { FormField } from './FormField';
import { useResendVerification } from '../hooks/useResendVerification';
import { forgotPasswordSchema } from '../validation/forgotPasswordSchema';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';

export function ResendVerificationForm({ defaultEmail = '' }) {
  const resendVerification = useResendVerification();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: {
      email: defaultEmail,
    },
  });

  const onSubmit = (values) => {
    resendVerification.mutate(values);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="grid gap-4">
      {resendVerification.error ? (
        <Alert variant="destructive">
          <AlertDescription>{resendVerification.error.message}</AlertDescription>
        </Alert>
      ) : null}

      {resendVerification.isSuccess ? (
        <Alert>
          <AlertDescription>Verification email sent again.</AlertDescription>
        </Alert>
      ) : null}

      <FormField
        id="email"
        label="Email"
        type="email"
        autoComplete="email"
        error={
          errors.email?.message || resendVerification.error?.fieldErrors?.email
        }
        registration={register('email')}
      />

      <Button type="submit" disabled={resendVerification.isPending}>
        {resendVerification.isPending ? 'Sending…' : 'Resend verification email'}
      </Button>
    </form>
  );
}
