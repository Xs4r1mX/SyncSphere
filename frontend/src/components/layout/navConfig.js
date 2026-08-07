import {
  Activity,
  ArrowLeftRight,
  Cloud,
  LayoutDashboard,
  Settings,
} from 'lucide-react';

import { PATHS } from '@/app/routes/paths';

export const MAIN_NAV_ITEMS = [
  {
    path: PATHS.DASHBOARD,
    label: 'Dashboard',
    icon: LayoutDashboard,
  },
  {
    path: PATHS.CLOUD_STORAGES,
    label: 'Cloud Storages',
    icon: Cloud,
  },
  {
    path: PATHS.TRANSFER_HISTORY,
    label: 'Transfer History',
    icon: ArrowLeftRight,
  },
  {
    path: PATHS.ACTIVITY,
    label: 'Activity',
    icon: Activity,
  },
];

export const FOOTER_NAV_ITEMS = [
  {
    path: PATHS.SETTINGS,
    label: 'Settings',
    icon: Settings,
  },
];
