export const TRANSFER_JOB_STATUSES = [
  'pending',
  'planning',
  'running',
  'success',
  'failed',
  'cancelled',
  'partial_success',
];

export const IN_FLIGHT_STATUSES = ['pending', 'planning', 'running'];

export const STATUS_FILTER_OPTIONS = [
  { value: 'all', label: 'All' },
  { value: 'pending', label: 'Pending' },
  { value: 'planning', label: 'Planning' },
  { value: 'running', label: 'Running' },
  { value: 'success', label: 'Success' },
  { value: 'partial_success', label: 'Partial success' },
  { value: 'failed', label: 'Failed' },
  { value: 'cancelled', label: 'Cancelled' },
];

export function isInFlightStatus(status) {
  return IN_FLIGHT_STATUSES.includes(status);
}

export function formatStatusLabel(status) {
  if (!status) {
    return 'Unknown';
  }

  return status
    .split('_')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');
}

export function getJobStatusVariant(status) {
  switch (status) {
    case 'success':
      return 'secondary';
    case 'failed':
      return 'destructive';
    case 'cancelled':
    case 'partial_success':
      return 'outline';
    default:
      return 'outline';
  }
}

export function formatOperationLabel(operation) {
  switch (operation) {
    case 'copy':
      return 'Copy';
    case 'move':
      return 'Move';
    case 'copy_all':
      return 'Copy folder';
    case 'move_all':
      return 'Move folder';
    default:
      return formatStatusLabel(operation);
  }
}
