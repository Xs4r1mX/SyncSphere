import { useMutation } from '@tanstack/react-query';
import { useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

import authApi from '../api/authApi';
import { setCredentials } from '../store/authSlice';
import { PATHS } from '@/app/routes/paths';
import tokenService from '@/services/storage/tokenService';

export function useLogin() {
  const dispatch = useDispatch();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: authApi.login,
    onSuccess: (data) => {
      tokenService.setTokens({
        access: data.access,
        refresh: data.refresh,
      });
      dispatch(setCredentials(data.user));
      toast.success('Logged in successfully');
      navigate(PATHS.DASHBOARD, { replace: true });
    },
  });
}
