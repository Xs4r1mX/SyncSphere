export const cloudQueryKeys = {
  all: ['cloud'],
  connections: () => [...cloudQueryKeys.all, 'connections'],
  connection: (uuid) => [...cloudQueryKeys.all, 'connection', uuid],
};
