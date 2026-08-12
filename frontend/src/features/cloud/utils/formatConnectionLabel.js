export function formatConnectionLabel(connection, { includeEmail = true } = {}) {
  if (!connection) {
    return 'Unknown storage';
  }

  const name = connection.display_name?.trim() || '';
  const email = connection.account_email?.trim() || '';
  const provider = connection.provider_label?.trim() || '';
  const nameIsEmail = Boolean(
    name && email && name.toLowerCase() === email.toLowerCase(),
  );

  if (name && !nameIsEmail) {
    if (includeEmail && email) {
      return `${name} (${email})`;
    }
    return name;
  }

  if (includeEmail && email) {
    return provider ? `${provider} — ${email}` : email;
  }

  return provider || name || email || 'Cloud storage';
}
