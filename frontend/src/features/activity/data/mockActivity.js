import { Cloud, Link2, Upload, UserPlus } from 'lucide-react';

export const mockActivityEntries = [
  {
    id: '1',
    title: 'Connected Google Drive',
    description: 'Linked user@gmail.com to your workspace.',
    timestamp: '2 hours ago',
    icon: Link2,
  },
  {
    id: '2',
    title: 'Transfer completed',
    description: 'Project Assets.zip moved to Dropbox successfully.',
    timestamp: 'Yesterday at 4:32 PM',
    icon: Upload,
  },
  {
    id: '3',
    title: 'Dropbox synced',
    description: 'Account metadata and quota refreshed.',
    timestamp: '3 days ago',
    icon: Cloud,
  },
  {
    id: '4',
    title: 'Account verified',
    description: 'Your email address was confirmed.',
    timestamp: '1 week ago',
    icon: UserPlus,
  },
];
