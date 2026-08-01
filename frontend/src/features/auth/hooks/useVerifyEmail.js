import { useQuery } from '@tanstack/react-query';

import authApi from '../api/authApi';

export function useVerifyEmail(token) {
  return useQuery({
    queryKey: ['auth', 'verify-email', token],
    queryFn: () => authApi.verifyEmail(token),
    enabled: Boolean(token),
    retry: false,
    staleTime: Infinity,
  });
}
