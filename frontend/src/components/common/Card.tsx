import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/utils/cn';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

const paddings = {
  none: '',
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
};

export const Card: React.FC<CardProps> = ({
  children,
  className,
  hover = false,
  padding = 'md',
}) => {
  const baseClasses = cn(
    'bg-white rounded-2xl shadow-sm border border-secondary-100',
    paddings[padding],
    hover && 'transition-all duration-300 hover:shadow-lg hover:border-secondary-200',
    className
  );

  if (hover) {
    return (
      <motion.div
        whileHover={{ y: -4 }}
        className={baseClasses}
      >
        {children}
      </motion.div>
    );
  }

  return <div className={baseClasses}>{children}</div>;
};

export default Card;
