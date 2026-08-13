import { getActivityActionLabel } from '../constants/actions';

export function formatRelativeTime(isoDate) {
  if (!isoDate) {
    return '—';
  }

  const date = new Date(isoDate);
  const diffMs = date.getTime() - Date.now();
  const absMs = Math.abs(diffMs);
  const minute = 60_000;
  const hour = 60 * minute;
  const day = 24 * hour;

  const formatter = new Intl.RelativeTimeFormat(undefined, { numeric: 'auto' });

  if (absMs < hour) {
    return formatter.format(Math.round(diffMs / minute), 'minute');
  }

  if (absMs < day) {
    return formatter.format(Math.round(diffMs / hour), 'hour');
  }

  if (absMs < 7 * day) {
    return formatter.format(Math.round(diffMs / day), 'day');
  }

  return new Intl.DateTimeFormat(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  }).format(date);
}

export function formatActivityTitle(entry) {
  if (entry?.title) {
    return entry.title;
  }
  return getActivityActionLabel(entry?.action);
}

export function formatResourceType(entryOrType) {
  if (entryOrType && typeof entryOrType === 'object') {
    if (entryOrType.resource_type_label) {
      return entryOrType.resource_type_label;
    }
    return formatResourceType(entryOrType.resource_type);
  }

  const resourceType = entryOrType;
  if (!resourceType) {
    return '—';
  }
  return resourceType.charAt(0).toUpperCase() + resourceType.slice(1);
}

export function formatProviderLabel(provider) {
  if (!provider) {
    return '—';
  }
  return provider.replaceAll('_', ' ');
}

export function formatActivityDescription(entry) {
  const parts = [];

  if (entry.resource_name) {
    parts.push(entry.resource_name);
  }

  if (entry.provider) {
    parts.push(entry.provider.replaceAll('_', ' '));
  }

  if (entry.status === 'failed') {
    parts.push('failed');
  }

  if (parts.length === 0) {
    const typeLabel = entry.resource_type_label || formatResourceType(entry.resource_type);
    return typeLabel !== '—' ? `${typeLabel} activity` : 'Workspace event';
  }

  return parts.join(' · ');
}

export function formatActivityClock(isoDate) {
  if (!isoDate) {
    return '—';
  }

  return new Intl.DateTimeFormat(undefined, {
    hour: 'numeric',
    minute: '2-digit',
  }).format(new Date(isoDate));
}

export function formatActivityDayLabel(isoDate) {
  if (!isoDate) {
    return 'Unknown date';
  }

  const date = new Date(isoDate);
  const today = new Date();
  const yesterday = new Date();
  yesterday.setDate(today.getDate() - 1);

  const sameDay = (a, b) =>
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate();

  if (sameDay(date, today)) {
    return 'Today';
  }

  if (sameDay(date, yesterday)) {
    return 'Yesterday';
  }

  return new Intl.DateTimeFormat(undefined, {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(date);
}

export function groupActivityByDay(items = []) {
  const groups = [];
  const indexByKey = new Map();

  for (const entry of items) {
    const key = entry.created_at
      ? new Date(entry.created_at).toDateString()
      : 'unknown';

    if (!indexByKey.has(key)) {
      indexByKey.set(key, groups.length);
      groups.push({
        key,
        label: formatActivityDayLabel(entry.created_at),
        items: [],
      });
    }

    groups[indexByKey.get(key)].items.push(entry);
  }

  return groups;
}
