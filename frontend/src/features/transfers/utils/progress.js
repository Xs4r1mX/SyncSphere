export function getTransferProgressPercent(job) {
  if (!job) {
    return 0;
  }

  if (job.total_bytes > 0) {
    return Math.min(
      Math.round((job.bytes_transferred / job.total_bytes) * 100),
      100,
    );
  }

  if (job.items_total > 0) {
    return Math.min(
      Math.round((job.items_completed / job.items_total) * 100),
      100,
    );
  }

  return job.status === 'success' ? 100 : 0;
}
