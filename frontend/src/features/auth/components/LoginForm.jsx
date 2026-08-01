import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link } from 'react-router-dom';

import { FormField } from './FormField';
import { useLogin } from '../hooks/useLogin';
import { loginSchema } from '../validation/loginSchema';
import { PATHS } from '@/app/routes/paths';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';

export function LoginForm() {
  const login = useLogin();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const onSubmit = (values) => {
    login.mutate(values);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="grid gap-4">
      {login.error ? (
        <Alert variant="destructive">
          <AlertDescription>{login.error.message}</AlertDescription>
        </Alert>
      ) : null}

      <FormField
        id="email"
        label="Email"
        type="email"
        autoComplete="email"
        error={errors.email?.message || login.error?.fieldErrors?.email}
        registration={register('email')}
      />

      <FormField
        id="password"
        label="Password"
        type="password"
        autoComplete="current-password"
        error={errors.password?.message || login.error?.fieldErrors?.password}
        registration={register('password')}
      />

      <div className="flex justify-end">
        <Link
          to={PATHS.FORGOT_PASSWORD}
          className="text-sm text-muted-foreground underline-offset-4 hover:underline"
        >
          Forgot password?
        </Link>
      </div>

      <Button type="submit" disabled={login.isPending}>
        {login.isPending ? 'Signing in…' : 'Sign in'}
      </Button>

      <p className="text-center text-sm text-muted-foreground">
        Don&apos;t have an account?{' '}
        <Link to={PATHS.REGISTER} className="underline-offset-4 hover:underline">
          Register
        </Link>
      </p>
    </form>
  );
}
