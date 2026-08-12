import { Badge } from '@/components/ui/badge';
import { getJobStatusVariant, formatStatusLabel } from '../constants/status';

export function TransferStatusBadge({ status }) {
  return (
    <Badge variant={getJobStatusVariant(status)}>
      {formatStatusLabel(status)}
    </Badge>
  );
}
