"use client";

import React, { useState, useEffect } from 'react';
import { useTranslations, useLocale } from 'next-intl';
import MandiFinder, { MandiOption } from "@/components/MandiFinder";
import MandiDetails from "@/components/MandiDetails";
import LanguageSwitcher from "@/components/LanguageSwitcher";
import { TrendingUp, Sprout, Tractor, BarChart3, Loader2, Leaf, ShieldCheck, BarChart2, TrendingDown, Smartphone, Menu, X } from "lucide-react";
import { useAuth } from '@/context/AuthContext';
import Link from 'next/link';

interface TickerItem {
  commodity: string;
  emoji: string;
  price_per_qtl: number;
  change_pct: number | null;
  is_live: boolean;
}

interface GlobalStats {
  mandis_tracked: number;
  states_covered: number;
  ai_accuracy: number;
}

export default function Home() {
  const t = useTranslations('Index');
  const locale = useLocale();
  const { user, logout, isAuthenticated } = useAuth();
  const [selectedMandi, setSelectedMandi] = useState<MandiOption | null>(null);
  const [forecastData, setForecastData] = useState<any[] | null>(null);
  const [isLoadingForecast, setIsLoadingForecast] = useState(false);
  const [tickerItems, setTickerItems] = useState<TickerItem[]>([]);
  const [globalStats, setGlobalStats] = useState<GlobalStats | null>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const detailsRef = React.useRef<HTMLDivElement>(null);

  const fetchTicker = async () => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/market/summary`);
      if (res.ok) {
        const json = await res.json();
        setTickerItems(json.items || []);
        if (json.global_stats) {
          setGlobalStats(json.global_stats);
        }
      }
    } catch (e) {
      // silently keep previous data
    }
  };

  useEffect(() => {
    fetchTicker();
    const interval = setInterval(fetchTicker, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedMandi && selectedMandi.commodity && selectedMandi.state) {
      setTimeout(() => {
        detailsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 100);

      const fetchForecast = async () => {
        setIsLoadingForecast(true);
        setForecastData(null);
        try {
          const url = new URL(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/predict/`);
          url.searchParams.append("commodity", selectedMandi.commodity!);
          if (selectedMandi.variety) {
            url.searchParams.append("variety", selectedMandi.variety);
          }
          if (selectedMandi.search_date) {
            url.searchParams.append("date", selectedMandi.search_date);
          }
          url.searchParams.append("state", selectedMandi.state!);
          url.searchParams.append("mandi", selectedMandi.mandi);
          url.searchParams.append("days", "7");
          if (selectedMandi.price_per_qtl) {
            url.searchParams.append("current_price", String(selectedMandi.price_per_qtl));
          }
          const response = await fetch(url.toString());
          if (response.ok) {
            const data = await response.json();
            setForecastData(data);
          }
        } catch (error) {
          console.error("Error fetching forecast:", error);
        } finally {
          setIsLoadingForecast(false);
        }
      };
      fetchForecast();
    } else {
      setForecastData(null);
    }
  }, [selectedMandi]);

  return (
    <div className="min-h-screen" style={{ background: 'var(--cream)' }}>

      {/* ── HERO HEADER ──────────────────────────────────────── */}
      <header style={{ background: 'linear-gradient(135deg, #0d3d1a 0%, #1a5c2a 50%, #0f5c25 100%)', color: '#fff', position: 'relative', overflow: 'hidden' }}>
        <svg style={{ position: 'absolute', top: '-40px', right: '5%', width: 320, opacity: 0.08, pointerEvents: 'none' }} viewBox="0 0 200 200" fill="white">
          <path d="M100 0 C100 0 200 80 100 200 C0 80 100 0 100 0Z" />
        </svg>
        <svg style={{ position: 'absolute', bottom: '-60px', left: '8%', width: 240, opacity: 0.08, transform: 'rotate(30deg)', pointerEvents: 'none' }} viewBox="0 0 200 200" fill="white">
          <path d="M100 0 C100 0 200 80 100 200 C0 80 100 0 100 0Z" />
        </svg>

        <nav style={{ position: 'relative', zIndex: 10, borderBottom: '1px solid rgba(255,255,255,0.1)' }} className="flex items-center justify-between px-4 md:px-8 py-4">
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ background: '#22a447' }}>
              <Leaf size={20} className="text-white" />
            </div>
            <span className="text-xl font-bold tracking-tight">ANSH-M</span>
            <span className="font-light ml-1 text-sm hidden sm:block" style={{ color: 'rgba(255,255,255,0.6)' }}>Agri-Intelligence</span>
          </div>
          <div className="flex items-center gap-3">
            <div className="hidden md:flex items-center gap-4 mr-4 text-sm" style={{ color: 'rgba(255,255,255,0.8)' }}>
              {isAuthenticated ? (
                <>
                  <span className="text-emerald-300 font-bold">Hello, {user?.name || 'User'}</span>
                  <Link href={`/${locale}/admin`} className="hover:text-white transition-colors flex items-center gap-1"><ShieldCheck size={14}/> Admin</Link>
                  <button onClick={logout} className="hover:text-white transition-colors">Logout</button>
                </>
              ) : (
                <>
                  <Link href={`/${locale}/login`} className="hover:text-white transition-colors">Login</Link>
                  <Link href={`/${locale}/register`} className="hover:text-white transition-colors">Register</Link>
                </>
              )}
            </div>
            <LanguageSwitcher />
            <div className="hidden sm:flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-semibold" style={{ background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)' }}>
              <span className="w-2 h-2 rounded-full bg-green-400 inline-block" />
              {t('nav.live_data')}
            </div>
            {/* Mobile Menu Toggle */}
            <button className="md:hidden p-2 text-white" aria-label="Toggle menu" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
                 {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </nav>

        {/* Mobile Menu Overlay */}
        {mobileMenuOpen && (
          <div className="md:hidden absolute top-[70px] left-0 right-0 p-5 shadow-xl z-50 border-b animate-fade-in" style={{ background: '#0f5c25', borderColor: 'rgba(255,255,255,0.1)' }}>
             <div className="flex flex-col gap-5 text-sm font-semibold" style={{ color: 'rgba(255,255,255,0.95)' }}>
                {isAuthenticated ? (
                  <>
                    <span className="text-emerald-300">Hello, {user?.name || 'User'}</span>
                    <Link href={`/${locale}/admin`} className="flex items-center gap-2 opacity-90 hover:opacity-100"><ShieldCheck size={16}/> Admin Console</Link>
                    <button onClick={() => { logout(); setMobileMenuOpen(false); }} className="text-left w-full opacity-90 hover:opacity-100">Logout</button>
                  </>
                ) : (
                  <>
                    <Link href={`/${locale}/login`} onClick={() => setMobileMenuOpen(false)} className="opacity-90 hover:opacity-100">Login to Account</Link>
                    <Link href={`/${locale}/register`} onClick={() => setMobileMenuOpen(false)} className="opacity-90 hover:opacity-100">Create New Account</Link>
                  </>
                )}
             </div>
          </div>
        )}

        <div style={{ position: 'relative', zIndex: 10 }} className="px-8 py-14 md:py-20 max-w-5xl">
          <p className="mb-3 text-xs font-bold tracking-widest uppercase" style={{ color: '#86efac' }}>{t('hero.platform')}</p>
          <h1 className="text-4xl md:text-5xl font-extrabold leading-tight mb-5 max-w-2xl">
            {t('hero.title')}<br />
            <span style={{ color: '#4ade80' }}>{t('hero.subtitle')}</span>
          </h1>
          <p className="text-base md:text-lg max-w-xl mb-8 leading-relaxed" style={{ color: 'rgba(255,255,255,0.75)' }}>
            {t('hero.description')}
          </p>
          <div className="flex gap-3 flex-wrap">
            <button className="btn-green flex items-center gap-2 text-sm px-5 py-2.5">
              <TrendingUp size={16} /> {t('hero.explore')}
            </button>
            <Link href={isAuthenticated ? `/${locale}/subscribe` : `/${locale}/register`} className="flex items-center gap-2 text-sm px-5 py-2.5 rounded-lg font-semibold transition-colors hover:bg-white/20" style={{ color: '#fff', border: '1px solid rgba(255,255,255,0.3)', background: 'rgba(255,255,255,0.1)' }}>
              <Smartphone size={16} /> {locale === 'ta' ? 'SMS அறிக்கை' : 'SMS Alerts'}
            </Link>
            <button className="flex items-center gap-2 text-sm px-5 py-2.5 rounded-lg font-semibold" style={{ color: '#fff', border: '2px solid rgba(255,255,255,0.35)', background: 'transparent' }}>
              <Sprout size={16} /> {t('hero.about')}
            </button>
          </div>

          <div className="flex gap-4 mt-10 flex-wrap">
            {[
              { label: t('stats.mandis'), value: globalStats ? `${globalStats.mandis_tracked}+` : '...' },
              { label: t('stats.accuracy'), value: globalStats ? `${globalStats.ai_accuracy}%` : '...' },
              { label: t('stats.states'), value: globalStats ? `${globalStats.states_covered}` : '...' },
            ].map((s, i) => (
              <div key={i} className="rounded-xl px-4 py-2 text-center" style={{ background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.15)' }}>
                <p className="text-2xl font-bold" style={{ color: '#4ade80' }}>{s.value}</p>
                <p className="text-xs mt-0.5" style={{ color: 'rgba(255,255,255,0.6)' }}>{s.label}</p>
              </div>
            ))}
          </div>
        </div>
      </header>

      {/* ── TICKER STRIP ─────────────────────────────────────── */}
      <div
        className="py-2 px-0 overflow-hidden text-xs font-semibold tracking-wide"
        style={{ background: '#22a447', color: '#fff' }}
      >
        {tickerItems.length === 0 ? (
          <div className="flex gap-8 px-6 animate-pulse">
            {['...'].map((_, i) => (
              <span key={i} className="whitespace-nowrap opacity-60">{t('ticker.loading')}</span>
            ))}
          </div>
        ) : (
          <div className="flex" style={{ animation: 'ticker-scroll 40s linear infinite', whiteSpace: 'nowrap' }}>
            {[...tickerItems, ...tickerItems].map((item, i) => {
              const up = item.change_pct !== null && item.change_pct >= 0;
              const changeStr = item.change_pct !== null
                ? `${up ? '+' : ''}${item.change_pct.toFixed(1)}%`
                : '';
              return (
                <span key={i} className="inline-flex items-center gap-1.5 px-6 border-r border-white/20">
                  <span>{item.emoji}</span>
                  <span>{(t as any).has(`commodities.${item.commodity}`) ? t(`commodities.${item.commodity}` as any) : item.commodity}</span>
                  <span className="font-bold">₹{item.price_per_qtl.toLocaleString('en-IN', { maximumFractionDigits: 0 })}{t('ticker.per_qtl')}</span>
                  {item.change_pct !== null && (
                    <span style={{ color: up ? '#bbf7d0' : '#fca5a5' }}>{changeStr}</span>
                  )}
                  {!item.is_live && (
                    <span style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.65rem' }}>{t('ticker.est')}</span>
                  )}
                </span>
              );
            })}
          </div>
        )}
      </div>

      {/* ── FEATURE STRIP ────────────────────────────────────── */}
      <section className="section-white py-10 px-8">
        <div className="max-w-5xl mx-auto">
          <p className="label-tag mb-2">{t('services.tag')}</p>
          <h2 className="text-2xl font-bold text-dark-g mb-6" style={{ color: 'var(--text-dark)' }}>
            {t('services.title')}
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
            {[
              { icon: <TrendingUp size={24} className="text-white" />, bg: 'var(--green-brand)', title: t('services.forecast.title'), desc: t('services.forecast.description') },
              { icon: <ShieldCheck size={24} className="text-white" />, bg: '#3b82f6', title: t('services.optimizer.title'), desc: t('services.optimizer.description') },
              { icon: <BarChart2 size={24} className="text-white" />, bg: '#8b5cf6', title: t('services.overview.title'), desc: t('services.overview.description') },
            ].map((f, i) => (
              <div key={i} className="eco-card p-5 flex gap-4 items-start animate-fade-in transition-all duration-300 hover:-translate-y-1 hover:shadow-lg hover:border-emerald-300">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 shadow-sm" style={{ background: f.bg }}>
                  {f.icon}
                </div>
                <div>
                  <h3 className="font-bold text-sm mb-1" style={{ color: 'var(--text-dark)' }}>{f.title}</h3>
                  <p className="text-xs leading-relaxed" style={{ color: 'var(--text-muted)' }}>{f.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── MANDI FINDER ─────────────────────────────────────── */}
      <section className="section-light py-10 px-8">
        <div className="max-w-5xl mx-auto">
          <p className="label-tag mb-2">{t('finder.tag')}</p>
          <h2 className="text-2xl font-bold mb-6" style={{ color: 'var(--text-dark)' }}>
            {t('finder.title')}
          </h2>
          <div className="relative z-[60]">
            <MandiFinder onSelectMandi={(mandi) => setSelectedMandi(mandi)} />
          </div>
        </div>
      </section>

      {/* ── DETAILED ANALYSIS ────────────────────────────────── */}
      <section className="section-white py-10 px-8" ref={detailsRef}>
        <div className="max-w-5xl mx-auto">
          {selectedMandi ? (
            <div className="eco-card p-6 animate-fade-in">
              <h2 className="text-lg font-bold mb-4 flex items-center gap-2" style={{ color: 'var(--text-dark)' }}>
                <BarChart3 className="text-brand" style={{ color: 'var(--green-brand)' }} />
                {t('analysis.title')}: {selectedMandi.translated_name || selectedMandi.mandi}
                {isLoadingForecast && <Loader2 className="animate-spin ml-2" size={18} style={{ color: 'var(--green-brand)' }} />}
              </h2>
              <MandiDetails mandi={selectedMandi} forecast={forecastData || undefined} />
            </div>
          ) : (
            <div className="eco-card p-12 text-center flex flex-col items-center justify-center min-h-[260px] relative overflow-hidden group border-dashed border-2 border-emerald-200">
              <div className="absolute inset-0 bg-emerald-50/50 group-hover:bg-emerald-50 transition-colors duration-500"></div>
              <div className="w-16 h-16 rounded-full flex items-center justify-center mb-4 relative z-10 transition-transform group-hover:scale-110 duration-500 shadow-sm border-2 border-emerald-300 bg-white">
                <Tractor size={30} className="text-emerald-500" />
              </div>
              <h2 className="text-lg font-bold mb-2" style={{ color: 'var(--text-dark)' }}>{t('analysis.ready')}</h2>
              <p className="max-w-md text-sm leading-relaxed" style={{ color: 'var(--text-muted)' }}>
                {t('finder.placeholder')}
              </p>
            </div>
          )}
        </div>
      </section>

      {/* ── FOOTER ───────────────────────────────────────────── */}
      <footer className="py-8 px-8 text-center" style={{ background: 'linear-gradient(135deg, #0d3d1a 0%, #1a5c2a 100%)', color: '#fff' }}>
        <div className="flex items-center justify-center gap-2 mb-2">
          <Leaf size={18} style={{ color: 'var(--green-light)' }} />
          <span className="font-bold tracking-wide">ANSH-M</span>
        </div>
        <p className="text-white/50 text-xs">{t('footer.tagline')}</p>
      </footer>
    </div>
  );
}
