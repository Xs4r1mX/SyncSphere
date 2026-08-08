const ERROR_MESSAGES = {
  access_denied: 'You cancelled the authorization request.',
  missing_code_or_state: 'The authorization response was incomplete.',
};

export function getOAuthErrorMessage(errorCode) {
  if (!errorCode) {
    return 'We could not connect your cloud storage account.';
  }

  return ERROR_MESSAGES[errorCode] || decodeURIComponent(errorCode);
}
