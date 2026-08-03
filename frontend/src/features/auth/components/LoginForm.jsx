import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link } from 'react-router-dom';
import { TriangleAlert } from 'lucide-react';

import { FormField } from './FormField';
import { useLogin } from '../hooks/useLogin';
import { loginSchema } from '../validation/loginSchema';
import { PATHS } from '@/app/routes/paths';
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

      <div className="flex items-center justify-between gap-3">
        {login.error ? (
          <p
            role="alert"
            className="flex min-w-0 items-center gap-1.5 text-sm text-destructive"
          >
            <TriangleAlert className="size-4 shrink-0" />
            <span className="truncate">{login.error.message}</span>
          </p>
        ) : (
          <span />
        )}
        <Link
          to={PATHS.FORGOT_PASSWORD}
          className="shrink-0 text-sm text-muted-foreground underline-offset-4 transition-colors hover:text-foreground hover:underline"
        >
          Forgot password?
        </Link>
      </div>

      <Button type="submit" disabled={login.isPending}>
        {login.isPending ? 'Signing in…' : 'Sign in'}
      </Button>

      <p className="text-center text-sm text-muted-foreground">
        Don&apos;t have an account?{' '}
        <Link
          to={PATHS.REGISTER}
          className="underline-offset-4 transition-colors hover:text-foreground hover:underline"
        >
          Register
        </Link>
      </p>
    </form>
  );
}
