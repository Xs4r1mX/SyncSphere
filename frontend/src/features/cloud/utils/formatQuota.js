const GB = 1024 ** 3;

export function formatBytesToGb(bytes) {
  if (bytes == null || Number.isNaN(Number(bytes))) {
    return null;
  }

  return Number((Number(bytes) / GB).toFixed(1));
}

export function formatQuotaLabel(usedBytes, totalBytes) {
  const used = formatBytesToGb(usedBytes);
  const total = formatBytesToGb(totalBytes);

  if (used == null && total == null) {
    return 'Quota unavailable';
  }

  if (total == null) {
    return `${used ?? 0} GB used`;
  }

  return `${used ?? 0} GB / ${total} GB`;
}

export function getQuotaPercentage(usedBytes, totalBytes) {
  if (usedBytes == null || totalBytes == null || totalBytes <= 0) {
    return 0;
  }

  return Math.min(Math.round((usedBytes / totalBytes) * 100), 100);
}
