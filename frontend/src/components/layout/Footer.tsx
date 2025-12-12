import React from 'react';
import { useTranslation } from 'react-i18next';
import { Logo } from '@/components/common';

export const Footer: React.FC = () => {
  const { t } = useTranslation();
  const currentYear = new Date().getFullYear();

  return (
    <footer className="border-t border-secondary-200 bg-white">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
          <div className="flex items-center gap-4">
            <Logo size="sm" />
            <p className="text-sm text-secondary-500">
              {t('footer.tagline')}
            </p>
          </div>
          <p className="text-sm text-secondary-400">
            {t('footer.copyright', { year: currentYear })}
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
