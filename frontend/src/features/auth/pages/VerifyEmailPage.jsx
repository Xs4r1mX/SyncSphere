import {
  CircleCheck,
  CircleX,
  LoaderCircle,
  MailCheck,
} from 'lucide-react';
import { Link, useLocation, useSearchParams } from 'react-router-dom';

import { ResendVerificationForm } from '../components/ResendVerificationForm';
import { useVerifyEmail } from '../hooks/useVerifyEmail';
import { PATHS } from '@/app/routes/paths';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { buttonVariants } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { cn } from '@/lib/utils';

function getStatus(token, verifyEmail) {
  if (!token) {
    return {
      icon: <MailCheck className="size-6" />,
      title: 'Check your email',
      description: 'Use the verification link we sent to activate your account.',
    };
  }

  if (verifyEmail.isPending || verifyEmail.isFetching) {
    return {
      icon: <LoaderCircle className="size-6 animate-spin" />,
      title: 'Verifying…',
      description: 'Please wait while we confirm your email address.',
    };
  }

  if (verifyEmail.isSuccess) {
    return {
      icon: <CircleCheck className="size-6 text-emerald-500" />,
      title: 'Email verified',
      description: 'Your account is ready. You can sign in now.',
    };
  }

  return {
    icon: <CircleX className="size-6 text-destructive" />,
    title: 'Verification failed',
    description:
      verifyEmail.error?.message ||
      'This verification link is invalid or has expired.',
  };
}

export function VerifyEmailPage() {
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') || '';
  const email =
    typeof location.state?.email === 'string' ? location.state.email : '';
  const verifyEmail = useVerifyEmail(token);
  const isWaitingForEmail = !token;
  const isVerifying = Boolean(token) && (verifyEmail.isPending || verifyEmail.isFetching);
  const status = getStatus(token, verifyEmail);

  return (
    <Card>
      <CardHeader className="justify-items-center text-center">
        <div className="mb-1 flex size-12 items-center justify-center rounded-full border border-border bg-muted">
          {status.icon}
        </div>
        <CardTitle>{status.title}</CardTitle>
        <CardDescription>{status.description}</CardDescription>
      </CardHeader>
      <CardContent className="grid gap-5" aria-live="polite">
        {isWaitingForEmail ? (
          <>
            <div className="grid gap-2 text-center text-sm text-muted-foreground">
              <p>
                We sent a verification email
                {email ? (
                  <>
                    {' to '}
                    <span className="font-medium text-foreground">{email}</span>
                  </>
                ) : null}
                .
              </p>
              <p>Open the email and select “Verify email” to continue.</p>
            </div>

            <ResendVerificationForm defaultEmail={email} />
          </>
        ) : null}

        {isVerifying ? (
          <p className="text-center text-sm text-muted-foreground">
            This will only take a moment…
          </p>
        ) : null}

        {verifyEmail.isSuccess ? (
          <Link
            to={PATHS.LOGIN}
            className={cn(buttonVariants(), 'w-full')}
          >
            Continue to sign in
          </Link>
        ) : null}

        {token && verifyEmail.isError ? (
          <div className="grid gap-4">
            <Alert variant="destructive">
              <AlertDescription>{verifyEmail.error.message}</AlertDescription>
            </Alert>
            <ResendVerificationForm />
          </div>
        ) : null}

        {isWaitingForEmail || (token && verifyEmail.isError) ? (
          <p className="text-center text-sm text-muted-foreground">
            Already verified?{' '}
            <Link
              to={PATHS.LOGIN}
              className="text-foreground underline-offset-4 hover:underline"
            >
              Sign in
            </Link>
          </p>
        ) : null}
      </CardContent>
    </Card>
  );
}
