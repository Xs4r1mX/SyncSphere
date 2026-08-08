const UNITS = ['B', 'KB', 'MB', 'GB', 'TB'];

export function formatFileSize(bytes) {
  if (bytes == null) {
    return '—';
  }

  if (bytes === 0) {
    return '0 B';
  }

  const unitIndex = Math.min(
    Math.floor(Math.log(bytes) / Math.log(1024)),
    UNITS.length - 1,
  );
  const value = bytes / 1024 ** unitIndex;

  return `${value >= 10 || unitIndex === 0 ? value.toFixed(0) : value.toFixed(1)} ${UNITS[unitIndex]}`;
}
