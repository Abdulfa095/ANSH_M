"use client";

import React from 'react';
import { useTranslations } from 'next-intl';
import { TrendingUp, AlertTriangle, CloudSun, Leaf } from "lucide-react";

const MarketOverview = () => {
    const t = useTranslations('MarketOverview');

    return (
        <div className="w-full bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10 shadow-xl">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-green-400 to-emerald-600">
                    {t('title')}
                </h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Insight 1: Market Demand */}
                <div className="bg-slate-800/50 p-4 rounded-lg flex items-start gap-4 border border-slate-700/50">
                    <div className="p-3 bg-blue-500/20 text-blue-400 rounded-lg">
                        <TrendingUp size={24} />
                    </div>
                    <div>
                        <h3 className="text-slate-300 font-semibold mb-1">{t('demand.title')}</h3>
                        <p className="text-sm text-slate-400">
                            {t('demand.description')}
                        </p>
                    </div>
                </div>

                {/* Insight 2: Weather Impact */}
                <div className="bg-slate-800/50 p-4 rounded-lg flex items-start gap-4 border border-slate-700/50">
                    <div className="p-3 bg-yellow-500/20 text-yellow-400 rounded-lg">
                        <CloudSun size={24} />
                    </div>
                    <div>
                        <h3 className="text-slate-300 font-semibold mb-1">{t('weather.title')}</h3>
                        <p className="text-sm text-slate-400">
                            {t('weather.description')}
                        </p>
                    </div>
                </div>

                {/* Insight 3: Price Stability */}
                <div className="bg-slate-800/50 p-4 rounded-lg flex items-start gap-4 border border-slate-700/50">
                    <div className="p-3 bg-emerald-500/20 text-emerald-400 rounded-lg">
                        <Leaf size={24} />
                    </div>
                    <div>
                        <h3 className="text-slate-300 font-semibold mb-1">{t('stable.title')}</h3>
                        <p className="text-sm text-slate-400">
                            {t('stable.description')}
                        </p>
                    </div>
                </div>

                {/* Insight 4: Transport Cost Warning */}
                <div className="bg-slate-800/50 p-4 rounded-lg flex items-start gap-4 border border-slate-700/50">
                    <div className="p-3 bg-red-500/20 text-red-400 rounded-lg">
                        <AlertTriangle size={24} />
                    </div>
                    <div>
                        <h3 className="text-slate-300 font-semibold mb-1">{t('transport.title')}</h3>
                        <p className="text-sm text-slate-400">
                            {t('transport.description')}
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MarketOverview;
