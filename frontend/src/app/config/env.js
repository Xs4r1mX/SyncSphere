import { z } from 'zod';

const envSchema = z.object({
  VITE_APP_NAME: z.string().min(1, 'VITE_APP_NAME is required'),
  VITE_API_BASE_URL: z
    .string()
    .url('VITE_API_BASE_URL must be a valid URL')
    .min(1, 'VITE_API_BASE_URL is required'),
  VITE_DEBUG: z
    .enum(['true', 'false'])
    .optional()
    .default('false'),
  VITE_API_TIMEOUT_MS: z
    .string()
    .optional()
    .default('30000')
    .transform((value) => Number(value))
    .refine((value) => Number.isFinite(value) && value > 0, {
      message: 'VITE_API_TIMEOUT_MS must be a positive number',
    }),
});

const parsed = envSchema.safeParse(import.meta.env);

if (!parsed.success) {
  const details = parsed.error.issues
    .map((issue) => `${issue.path.join('.')}: ${issue.message}`)
    .join('\n');

  throw new Error(`Invalid environment configuration:\n${details}`);
}

const env = {
  appName: parsed.data.VITE_APP_NAME,
  apiBaseUrl: parsed.data.VITE_API_BASE_URL.replace(/\/$/, ''),
  debug: parsed.data.VITE_DEBUG === 'true',
  apiTimeoutMs: parsed.data.VITE_API_TIMEOUT_MS,
};

export default env;
