import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export function FormField({
  id,
  label,
  error,
  type = 'text',
  autoComplete,
  registration,
  ...props
}) {
  return (
    <div className="grid gap-2">
      <Label htmlFor={id}>{label}</Label>
      <Input
        id={id}
        type={type}
        autoComplete={autoComplete}
        aria-invalid={Boolean(error)}
        {...registration}
        {...props}
      />
      {error ? <p className="text-sm text-destructive">{error}</p> : null}
    </div>
  );
}
