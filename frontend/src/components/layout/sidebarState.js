const SIDEBAR_COOKIE_NAME = 'sidebar_state';

export function getSidebarDefaultOpen() {
  if (typeof document === 'undefined') {
    return true;
  }

  const match = document.cookie.match(
    new RegExp(`(?:^|;\\s*)${SIDEBAR_COOKIE_NAME}=(true|false)`),
  );

  return match ? match[1] === 'true' : true;
}
