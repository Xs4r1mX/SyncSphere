import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link } from 'react-router-dom';
import { CircleCheck, TriangleAlert } from 'lucide-react';

import { FormField } from './FormField';
import { useForgotPassword } from '../hooks/useForgotPassword';
import { forgotPasswordSchema } from '../validation/forgotPasswordSchema';
import { PATHS } from '@/app/routes/paths';
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

      {forgotPassword.error ? (
        <p
          role="alert"
          className="flex items-center gap-1.5 text-sm text-destructive"
        >
          <TriangleAlert className="size-4 shrink-0" />
          <span>{forgotPassword.error.message}</span>
        </p>
      ) : null}

      {forgotPassword.isSuccess ? (
        <p
          role="status"
          className="flex items-start gap-1.5 text-sm text-foreground"
        >
          <CircleCheck className="mt-0.5 size-4 shrink-0" />
          <span>{forgotPassword.data?.message}</span>
        </p>
      ) : null}

      <Button type="submit" disabled={forgotPassword.isPending}>
        {forgotPassword.isPending ? 'Sending…' : 'Send reset link'}
      </Button>

      <p className="text-center text-sm text-muted-foreground">
        <Link
          to={PATHS.LOGIN}
          className="underline-offset-4 transition-colors hover:text-foreground hover:underline"
        >
          Back to sign in
        </Link>
      </p>
    </form>
  );
}
