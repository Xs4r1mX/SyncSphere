import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link } from 'react-router-dom';

import { FormField } from './FormField';
import { useRegister } from '../hooks/useRegister';
import { registerSchema } from '../validation/registerSchema';
import { PATHS } from '@/app/routes/paths';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';

export function RegisterForm() {
  const registerMutation = useRegister();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      first_name: '',
      last_name: '',
      email: '',
      password: '',
    },
  });

  const onSubmit = (values) => {
    registerMutation.mutate(values);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="grid gap-4">
      {registerMutation.error ? (
        <Alert variant="destructive">
          <AlertDescription>{registerMutation.error.message}</AlertDescription>
        </Alert>
      ) : null}

      <div className="grid gap-4 sm:grid-cols-2">
        <FormField
          id="first_name"
          label="First name"
          autoComplete="given-name"
          error={
            errors.first_name?.message ||
            registerMutation.error?.fieldErrors?.first_name
          }
          registration={register('first_name')}
        />
        <FormField
          id="last_name"
          label="Last name"
          autoComplete="family-name"
          error={
            errors.last_name?.message ||
            registerMutation.error?.fieldErrors?.last_name
          }
          registration={register('last_name')}
        />
      </div>

      <FormField
        id="email"
        label="Email"
        type="email"
        autoComplete="email"
        error={errors.email?.message || registerMutation.error?.fieldErrors?.email}
        registration={register('email')}
      />

      <FormField
        id="password"
        label="Password"
        type="password"
        autoComplete="new-password"
        error={
          errors.password?.message || registerMutation.error?.fieldErrors?.password
        }
        registration={register('password')}
      />

      <Button type="submit" disabled={registerMutation.isPending}>
        {registerMutation.isPending ? 'Creating account…' : 'Create account'}
      </Button>

      <p className="text-center text-sm text-muted-foreground">
        Already have an account?{' '}
        <Link to={PATHS.LOGIN} className="underline-offset-4 hover:underline">
          Sign in
        </Link>
      </p>
    </form>
  );
}
