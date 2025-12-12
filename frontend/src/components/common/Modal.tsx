import React from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { X } from 'lucide-react';
import { Button } from './Button';
import { cn } from '@/utils/cn';

type ModalProps = {
  isOpen: boolean;
  onClose: () => void;
  title?: React.ReactNode;
  description?: React.ReactNode;
  children?: React.ReactNode;
  primaryAction?: {
    label: string;
    onClick: () => void | Promise<void>;
    isLoading?: boolean;
    variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  };
  secondaryAction?: {
    label: string;
    onClick: () => void | Promise<void>;
    isLoading?: boolean;
    variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  };
  widthClass?: string;
  className?: string;
};

const backdropVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 },
};

const dialogVariants = {
  hidden: { opacity: 0, scale: 0.95, y: 10 },
  visible: { opacity: 1, scale: 1, y: 0 },
};

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  description,
  children,
  primaryAction,
  secondaryAction,
  widthClass = 'max-w-lg',
  className,
}) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center px-4"
          initial="hidden"
          animate="visible"
          exit="hidden"
          variants={backdropVariants}
          transition={{ duration: 0.15 }}
        >
          <div
            className="absolute inset-0 bg-black/40 backdrop-blur-sm"
            onClick={onClose}
            aria-hidden
          />
          <motion.div
            role="dialog"
            aria-modal="true"
            className={cn(
              'relative z-10 w-full rounded-2xl bg-white shadow-2xl',
              'border border-secondary-200',
              widthClass,
              className
            )}
            variants={dialogVariants}
            transition={{ duration: 0.18 }}
          >
            <div className="flex items-start justify-between px-5 py-4 border-b border-secondary-200">
              <div>
                {title && <h3 className="text-lg font-semibold text-secondary-900">{title}</h3>}
                {description && <p className="text-sm text-secondary-600 mt-1">{description}</p>}
              </div>
              <button
                onClick={onClose}
                className="rounded-full p-1.5 text-secondary-500 hover:bg-secondary-100 transition"
                aria-label="Close modal"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {children && <div className="px-5 py-4">{children}</div>}

            {(primaryAction || secondaryAction) && (
              <div className="flex justify-end gap-2 px-5 py-4 border-t border-secondary-200 bg-secondary-50 rounded-b-2xl">
                {secondaryAction && (
                  <Button
                    variant={secondaryAction.variant || 'ghost'}
                    onClick={secondaryAction.onClick}
                    isLoading={secondaryAction.isLoading}
                  >
                    {secondaryAction.label}
                  </Button>
                )}
                {primaryAction && (
                  <Button
                    variant={primaryAction.variant || 'primary'}
                    onClick={primaryAction.onClick}
                    isLoading={primaryAction.isLoading}
                  >
                    {primaryAction.label}
                  </Button>
                )}
              </div>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default Modal;
