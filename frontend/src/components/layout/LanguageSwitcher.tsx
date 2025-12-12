import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import { Globe, ChevronDown, Check } from 'lucide-react';
import { Language, LanguageOption } from '@/types';
import { cn } from '@/utils/cn';

const languages: LanguageOption[] = [
  { code: 'en', name: 'English', flag: '🇬🇧' },
  { code: 'hu', name: 'Magyar', flag: '🇭🇺' },
  { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
];

interface LanguageSwitcherProps {
  variant?: 'default' | 'compact';
}

export const LanguageSwitcher: React.FC<LanguageSwitcherProps> = ({
  variant = 'default',
}) => {
  const { i18n } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const currentLanguage = languages.find((lang) => lang.code === i18n.language) || languages[0];

  const handleLanguageChange = (code: Language) => {
    i18n.changeLanguage(code);
    localStorage.setItem('ingazo_language', code);
    setIsOpen(false);
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          'flex items-center gap-2 rounded-xl px-3 py-2 transition-all duration-200',
          'hover:bg-secondary-100 focus:outline-none focus:ring-2 focus:ring-primary-500/20',
          isOpen && 'bg-secondary-100'
        )}
      >
        {variant === 'compact' ? (
          <>
            <span className="text-lg">{currentLanguage.flag}</span>
            <ChevronDown className={cn(
              'h-4 w-4 text-secondary-500 transition-transform duration-200',
              isOpen && 'rotate-180'
            )} />
          </>
        ) : (
          <>
            <Globe className="h-5 w-5 text-secondary-500" />
            <span className="text-sm font-medium text-secondary-700">
              {currentLanguage.code.toUpperCase()}
            </span>
            <ChevronDown className={cn(
              'h-4 w-4 text-secondary-500 transition-transform duration-200',
              isOpen && 'rotate-180'
            )} />
          </>
        )}
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.15 }}
            className="absolute right-0 top-full z-50 mt-2 w-48 overflow-hidden rounded-xl border border-secondary-200 bg-white shadow-lg"
          >
            {languages.map((language) => (
              <button
                key={language.code}
                onClick={() => handleLanguageChange(language.code)}
                className={cn(
                  'flex w-full items-center gap-3 px-4 py-3 text-left transition-colors',
                  'hover:bg-secondary-50',
                  currentLanguage.code === language.code && 'bg-primary-50'
                )}
              >
                <span className="text-xl">{language.flag}</span>
                <span className="flex-1 text-sm font-medium text-secondary-700">
                  {language.name}
                </span>
                {currentLanguage.code === language.code && (
                  <Check className="h-4 w-4 text-primary-500" />
                )}
              </button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default LanguageSwitcher;
