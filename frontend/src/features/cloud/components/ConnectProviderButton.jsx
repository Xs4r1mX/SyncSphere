import { ChevronDown, Plus } from 'lucide-react';

import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { cloudProviders } from '../constants/providers';

export function ConnectProviderButton({ onConnect, connectingProviderId, disabled }) {
  const availableProviders = cloudProviders.filter((provider) => provider.available);

  if (availableProviders.length === 0) {
    return (
      <Button disabled>
        <Plus />
        Connect storage
      </Button>
    );
  }

  if (availableProviders.length === 1) {
    const provider = availableProviders[0];
    return (
      <Button
        disabled={disabled}
        onClick={() => onConnect(provider.id)}
      >
        <Plus />
        {connectingProviderId === provider.id ? 'Connecting…' : 'Connect storage'}
      </Button>
    );
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        render={
          <Button disabled={disabled}>
            <Plus />
            Connect storage
            <ChevronDown className="size-4 opacity-70" />
          </Button>
        }
      />
      <DropdownMenuContent align="end">
        {availableProviders.map((provider) => (
          <DropdownMenuItem
            key={provider.id}
            disabled={connectingProviderId === provider.id}
            onClick={() => onConnect(provider.id)}
          >
            {connectingProviderId === provider.id
              ? `Connecting ${provider.name}…`
              : provider.name}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
