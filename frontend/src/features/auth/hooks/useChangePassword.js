import { useMutation } from '@tanstack/react-query';
import { useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

import authApi from '../api/authApi';
import { setUnauthenticated } from '../store/authSlice';
import { PATHS } from '@/app/routes/paths';
import tokenService from '@/services/storage/tokenService';

export function useChangePassword() {
  const dispatch = useDispatch();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: ({ old_password, new_password }) =>
      authApi.changePassword({ old_password, new_password }),
    onSuccess: () => {
      tokenService.clearTokens();
      dispatch(setUnauthenticated());
      toast.success('Password changed. Please log in again.');
      navigate(PATHS.LOGIN, { replace: true });
    },
  });
}
