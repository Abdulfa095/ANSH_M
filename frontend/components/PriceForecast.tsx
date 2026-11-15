"use client";

import React, { useMemo } from 'react';
import { useTranslations, useLocale } from 'next-intl';
import {
    ResponsiveContainer, ComposedChart, CartesianGrid, XAxis, YAxis, Tooltip, Legend, Area, Line
} from 'recharts';
import { TrendingUp, TrendingDown, Sparkles, AlertTriangle } from 'lucide-react';

interface ForecastData {
    date: string;
    price_p10: number;
    price_p50: number;
    price_p90: number;
    is_extreme: boolean;
    reason?: string;
}

interface PriceForecastProps {
    forecast: ForecastData[];
}

const PriceForecast: React.FC<PriceForecastProps> = ({ forecast }) => {
    const t = useTranslations('MandiDetails');
    const locale = useLocale();

    const hasExtremeRisk = forecast.some(f => f.is_extreme);
    const forecastReason = forecast.length > 0 ? forecast[forecast.length - 1].reason : null;

    const forecastChartData = useMemo(() => {
        return forecast.map(f => {
            const dateObj = new Date(f.date);
            return {
                ...f,
                formattedDate: dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
                range: [f.price_p10, f.price_p90]
            };
        });
    }, [forecast]);

    const { forecastChangePct, forecastMaxHigh, isForecastUp } = useMemo(() => {
        if (forecastChartData.length === 0) return { forecastChangePct: 0, forecastMaxHigh: 0, isForecastUp: true };
        const start = forecastChartData[0].price_p50;
        const end = forecastChartData[forecastChartData.length - 1].price_p50;
        const changePct = start > 0 ? ((end - start) / start) * 100 : 0;
        const maxHigh = Math.max(...forecastChartData.map(d => d.price_p90));
        return { forecastChangePct: changePct, forecastMaxHigh: maxHigh, isForecastUp: changePct >= 0 };
    }, [forecastChartData]);

    if (forecastChartData.length === 0) return null;

    return (
        <div className="flex flex-col gap-8 w-full animate-fade-in">
            {/* EXTREME VOLATILITY ALERT */}
            {hasExtremeRisk && (
                <div className="bg-red-500/20 border border-red-500/50 p-4 rounded-xl flex items-center gap-4 animate-pulse">
                    <AlertTriangle className="text-red-500 w-8 h-8 flex-shrink-0" />
                    <div>
                        <h4 className="text-red-400 font-bold text-lg">{t('volatility.title')}</h4>
                        <p className="text-red-200/80 text-sm">
                            {t('volatility.description')}
                        </p>
                    </div>
                </div>
            )}

            {/* AI FUTURE TREND DASHBOARD */}
            <div className="eco-card overflow-hidden group mb-8 bg-white shadow-sm border border-gray-100 flex flex-col">
                <div className="p-5 border-b border-gray-100 bg-gray-50/50 flex items-center justify-between">
                    <h4 className="font-semibold text-lg flex items-center gap-2 text-gray-800">
                        <TrendingUp size={20} className="text-emerald-500" /> {t('forecast.title')}
                    </h4>
                    <span className="text-xs px-3 py-1 rounded-full border bg-emerald-50 text-emerald-700 border-emerald-200 shadow-sm font-medium">
                        {t('forecast.autoregressive')}
                    </span>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-4 divide-y lg:divide-y-0 lg:divide-x divide-gray-100 relative">
                    <div className="lg:col-span-3 p-6 relative">
                        <div className="absolute top-0 left-0 w-64 h-64 rounded-full blur-3xl -ml-16 -mt-16 transition-all duration-700 bg-emerald-50/50 pointer-events-none"></div>
                        
                        <div className="h-[320px] w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <ComposedChart data={forecastChartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                                    <defs>
                                        <linearGradient id="colorP50" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                                        </linearGradient>
                                        <linearGradient id="colorUncertainty" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#10b981" stopOpacity={0.15} />
                                            <stop offset="95%" stopColor="#10b981" stopOpacity={0.02} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" vertical={false} />
                                    <XAxis
                                        dataKey="formattedDate"
                                        tick={{ fill: '#6b7280', fontSize: 12 }}
                                        axisLine={false}
                                        tickLine={false}
                                        dy={10}
                                    />
                                    <YAxis
                                        domain={['dataMin - 500', 'dataMax + 500']}
                                        tick={{ fill: '#6b7280', fontSize: 12 }}
                                        axisLine={false}
                                        tickLine={false}
                                        tickFormatter={(val) => `₹${val}`}
                                        width={60}
                                    />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e5e7eb', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                        itemStyle={{ color: '#374151' }}
                                        labelStyle={{ color: '#6b7280', marginBottom: '4px', fontWeight: 'bold' }}
                                        formatter={(value: any, name: any) => {
                                            if (name === "price_p50") return [`₹${Number(value).toLocaleString('en-IN', { maximumFractionDigits: 2 })}`, t('forecast.expected')];
                                            if (name === "price_p90") return [`₹${Number(value).toLocaleString('en-IN', { maximumFractionDigits: 2 })}`, t('forecast.high')];
                                            if (name === "price_p10") return [`₹${Number(value).toLocaleString('en-IN', { maximumFractionDigits: 2 })}`, t('forecast.low')];
                                            return [value, name];
                                        }}
                                    />
                                    <Legend 
                                        wrapperStyle={{ paddingTop: '20px', color: '#374151' }} 
                                        formatter={(value) => <span className="mr-5 ml-1 font-medium">{value}</span>}
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="price_p90"
                                        stroke="none"
                                        fill="url(#colorUncertainty)"
                                        name={t('forecast.uncertainty')}
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="price_p10"
                                        stroke="none"
                                        fill="#ffffff"
                                        fillOpacity={1}
                                        activeDot={false}
                                        tooltipType="none"
                                        legendType="none"
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="price_p50"
                                        stroke="#22c55e"
                                        strokeWidth={4}
                                        dot={{ fill: '#16a34a', strokeWidth: 2, r: 4 }}
                                        activeDot={{ r: 6, fill: '#4ade80', stroke: '#fff', strokeWidth: 2 }}
                                        name={t('forecast.predicted')}
                                        style={{ filter: 'drop-shadow(0px 4px 4px rgba(34,164,71,0.2))' }}
                                    />
                                </ComposedChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    <div className="p-6 bg-gray-50/30 flex flex-col justify-center gap-8">
                        <div>
                            <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2 flex items-center gap-1">
                                7-Day Trend
                            </p>
                            <div className="flex items-end gap-2">
                                <span className={`text-3xl font-extrabold tracking-tight ${isForecastUp ? 'text-emerald-500' : 'text-red-500'}`}>
                                    {isForecastUp ? '+' : ''}{forecastChangePct.toFixed(1)}%
                                </span>
                                {isForecastUp ? <TrendingUp className="text-emerald-500 mb-1" size={24}/> : <TrendingDown className="text-red-500 mb-1" size={24}/>}
                            </div>
                        </div>

                        <div>
                            <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">
                                Projected Peak
                            </p>
                            <div className="text-2xl font-bold text-gray-800 font-mono">
                                ₹{forecastMaxHigh.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                            </div>
                        </div>

                        {forecastReason && (
                            <div className="mt-2 p-4 bg-white rounded-xl border border-blue-100 shadow-sm relative overflow-hidden group-hover:shadow-md transition-shadow">
                                <div className="absolute top-0 left-0 w-1 h-full bg-blue-400"></div>
                                <h5 className="text-xs font-bold text-blue-600 mb-2 flex items-center gap-1.5 uppercase tracking-wide">
                                    <Sparkles size={14} className="text-blue-500" /> DeepExtrema AI
                                </h5>
                                <p className="text-gray-600 text-sm italic leading-relaxed">
                                    "{(() => {
                                        if (locale === 'ta' && forecastReason.includes('model projects a')) {
                                            const match = forecastReason.match(/([-+]\d+\.\d+%)/);
                                            const pct = match ? match[1] : '';
                                            let t_text = `முந்தையத் தரவுகளின் அடிப்படையில் AI மாடல் ${pct} விலை மாற்றத்தை கணித்துள்ளது.`;
                                            if (forecastReason.includes('anomaly conditions')) {
                                                t_text += ' இதனுடன் வழக்கத்திற்கு மாறான சந்தை அசைவுகள் இருக்கலாம் என DeepExtrema எச்சரிக்கிறது.';
                                            }
                                            return t_text;
                                        }
                                        return forecastReason;
                                    })()}"
                                </p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PriceForecast;
