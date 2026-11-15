"use client";

import { useLocale } from 'next-intl';
import { useRouter, usePathname } from '../i18n/routing';
import { Globe } from 'lucide-react';

export default function LanguageSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  const toggleLocale = () => {
    const nextLocale = locale === 'en' ? 'ta' : 'en';
    router.replace(pathname, { locale: nextLocale });
  };

  return (
    <button
      onClick={toggleLocale}
      className="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold transition-all hover:bg-white/20 active:scale-95"
      style={{ 
        background: 'rgba(255,255,255,0.1)', 
        border: '1px solid rgba(255,255,255,0.2)',
        color: '#fff'
      }}
      title={locale === 'en' ? 'தமிழ் மாற்றவும்' : 'Switch to English'}
    >
      <Globe size={14} className="text-green-400" />
      <span>{locale === 'en' ? 'தமிழ்' : 'English'}</span>
    </button>
  );
}
