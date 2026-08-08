const UUID_PATTERN =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

export function isValidConnectionUuid(uuid) {
  return typeof uuid === 'string' && UUID_PATTERN.test(uuid);
}

export function getMockConnection(uuid) {
  if (!isValidConnectionUuid(uuid)) {
    return null;
  }

  return {
    uuid,
    display_name: 'Google Drive',
    account_email: 'user@gmail.com',
    provider_label: 'Google Drive',
    status: 'active',
    quota_used_bytes: 12_884_901_888,
    quota_total_bytes: 161_061_273_600,
  };
}
