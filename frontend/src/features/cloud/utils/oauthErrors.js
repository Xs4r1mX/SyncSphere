const ERROR_MESSAGES = {
  access_denied: 'You cancelled the authorization request.',
  missing_code_or_state: 'The authorization response was incomplete.',
  consent_required: 'Additional Microsoft consent is required for this account.',
  admin_consent_required: 'Your organization requires admin approval before connecting OneDrive.',
  interaction_required: 'Sign in again to finish connecting your cloud storage.',
  login_required: 'Sign in again to finish connecting your cloud storage.',
};

export function getOAuthErrorMessage(errorCode) {
  if (!errorCode) {
    return 'We could not connect your cloud storage account.';
  }

  return ERROR_MESSAGES[errorCode] || decodeURIComponent(errorCode);
}
