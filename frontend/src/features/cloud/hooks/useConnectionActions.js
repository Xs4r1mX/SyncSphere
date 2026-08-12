import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

import cloudApi from '../api/cloudApi';
import { cloudQueryKeys } from '../constants/queryKeys';

export function useUpdateConnection() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ uuid, displayName }) =>
      cloudApi.updateConnection(uuid, { display_name: displayName }),
    onSuccess: (connection) => {
      queryClient.invalidateQueries({ queryKey: cloudQueryKeys.connections() });
      queryClient.invalidateQueries({
        queryKey: cloudQueryKeys.connection(connection.uuid),
      });
      toast.success('Connection renamed.');
    },
    onError: (error) => {
      toast.error(error.message || 'Could not rename connection.');
    },
  });
}

export function useDisableConnection() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (uuid) => cloudApi.disableConnection(uuid),
    onSuccess: (connection) => {
      queryClient.invalidateQueries({ queryKey: cloudQueryKeys.connections() });
      queryClient.invalidateQueries({
        queryKey: cloudQueryKeys.connection(connection.uuid),
      });
      toast.success('Connection disabled.');
    },
    onError: (error) => {
      toast.error(error.message || 'Could not disable connection.');
    },
  });
}

export function useEnableConnection() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (uuid) => cloudApi.enableConnection(uuid),
    onSuccess: (connection) => {
      queryClient.invalidateQueries({ queryKey: cloudQueryKeys.connections() });
      queryClient.invalidateQueries({
        queryKey: cloudQueryKeys.connection(connection.uuid),
      });
      toast.success('Connection enabled.');
    },
    onError: (error) => {
      toast.error(error.message || 'Could not enable connection.');
    },
  });
}

export function useCheckConnectionHealth() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (uuid) => cloudApi.getConnectionHealth(uuid),
    onSuccess: (health) => {
      queryClient.invalidateQueries({ queryKey: cloudQueryKeys.connections() });
      queryClient.invalidateQueries({
        queryKey: cloudQueryKeys.connection(health.uuid),
      });

      if (health.is_healthy) {
        toast.success('Connection is healthy.');
        return;
      }

      toast.error('Connection health check failed.');
    },
    onError: (error) => {
      toast.error(error.message || 'Could not check connection health.');
    },
  });
}
