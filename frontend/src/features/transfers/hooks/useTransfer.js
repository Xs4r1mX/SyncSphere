import { useQuery } from '@tanstack/react-query';

import transferApi from '../api/transferApi';
import { transferQueryKeys } from '../constants/queryKeys';
import { isInFlightStatus } from '../constants/status';

export function useTransfer(jobUuid) {
  return useQuery({
    queryKey: transferQueryKeys.job(jobUuid),
    queryFn: () => transferApi.getTransfer(jobUuid),
    enabled: Boolean(jobUuid),
    refetchInterval: (query) =>
      isInFlightStatus(query.state.data?.status) ? 2000 : false,
  });
}

export function useTransferItems(jobUuid, { poll } = {}) {
  return useQuery({
    queryKey: transferQueryKeys.items(jobUuid),
    queryFn: () => transferApi.listTransferItems(jobUuid),
    enabled: Boolean(jobUuid),
    refetchInterval: poll ? 2000 : false,
  });
}
