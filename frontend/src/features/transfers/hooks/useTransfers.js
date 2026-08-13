import { useQuery } from '@tanstack/react-query';

import transferApi from '../api/transferApi';
import { transferQueryKeys } from '../constants/queryKeys';
import { isInFlightStatus } from '../constants/status';

function normalizeTransferList(data) {
  if (Array.isArray(data)) {
    return data;
  }
  return data?.items ?? [];
}

export function useTransfers(status) {
  const statusParam = status && status !== 'all' ? status : undefined;

  return useQuery({
    queryKey: transferQueryKeys.list(statusParam ?? 'all'),
    queryFn: async () => {
      const data = await transferApi.listTransfers(
        statusParam ? { status: statusParam } : {},
      );
      return normalizeTransferList(data);
    },
    refetchInterval: (query) => {
      const jobs = query.state.data ?? [];
      return jobs.some((job) => isInFlightStatus(job.status)) ? 3000 : false;
    },
  });
}
