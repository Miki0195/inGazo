import React from 'react';
import { Car } from 'lucide-react';
import { cn } from '@/utils/cn';

interface LogoProps {
  size?: 'sm' | 'md' | 'lg';
  showText?: boolean;
  className?: string;
}

const sizes = {
  sm: { icon: 'h-6 w-6', text: 'text-lg' },
  md: { icon: 'h-8 w-8', text: 'text-xl' },
  lg: { icon: 'h-10 w-10', text: 'text-2xl' },
};

export const Logo: React.FC<LogoProps> = ({
  size = 'md',
  showText = true,
  className,
}) => {
  return (
    <div className={cn('flex items-center gap-2', className)}>
      <div className="relative">
        <div className={cn(
          'flex items-center justify-center rounded-xl bg-gradient-to-br from-primary-400 to-primary-600 p-2 text-white shadow-lg shadow-primary-500/30',
          size === 'sm' && 'p-1.5',
          size === 'lg' && 'p-2.5'
        )}>
          <Car className={sizes[size].icon} />
        </div>
      </div>
      {showText && (
        <span className={cn(
          'font-bold bg-gradient-to-r from-primary-500 to-primary-700 bg-clip-text text-transparent',
          sizes[size].text
        )}>
          InGazo
        </span>
      )}
    </div>
  );
};

export default Logo;
