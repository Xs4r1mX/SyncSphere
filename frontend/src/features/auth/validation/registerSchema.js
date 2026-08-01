import { z } from 'zod';
import { passwordSchema } from './passwordRules';

export const registerSchema = z.object({
  first_name: z.string().trim().min(1, 'First name is required'),
  last_name: z.string().trim().min(1, 'Last name is required'),
  email: z
    .string()
    .min(1, 'Email is required')
    .email('Enter a valid email'),
  password: passwordSchema,
});
