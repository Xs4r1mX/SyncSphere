import { Link, useSearchParams } from 'react-router-dom';

import { ResendVerificationForm } from '../components/ResendVerificationForm';
import { useVerifyEmail } from '../hooks/useVerifyEmail';
import { PATHS } from '@/app/routes/paths';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';

export function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') || '';
  const verifyEmail = useVerifyEmail(token);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Verify email</CardTitle>
        <CardDescription>
          Confirm your email address to activate your account.
        </CardDescription>
      </CardHeader>
      <CardContent className="grid gap-4">
        {!token ? (
          <Alert variant="destructive">
            <AlertDescription>
              This verification link is invalid or missing a token.
            </AlertDescription>
          </Alert>
        ) : null}

        {token && verifyEmail.isPending ? (
          <p className="text-sm text-muted-foreground">Verifying your email…</p>
        ) : null}

        {verifyEmail.isSuccess ? (
          <div className="grid gap-4">
            <Alert>
              <AlertDescription>
                Email verified successfully
                {verifyEmail.data?.email ? ` for ${verifyEmail.data.email}` : ''}.
                You can now sign in.
              </AlertDescription>
            </Alert>
            <Link to={PATHS.LOGIN}>
              <Button type="button" className="w-full">
                Continue to sign in
              </Button>
            </Link>
          </div>
        ) : null}

        {verifyEmail.isError ? (
          <div className="grid gap-4">
            <Alert variant="destructive">
              <AlertDescription>{verifyEmail.error.message}</AlertDescription>
            </Alert>
            <ResendVerificationForm />
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}
