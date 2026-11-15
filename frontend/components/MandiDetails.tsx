"use client";

import React, { useMemo } from 'react';
import { useTranslations, useLocale } from 'next-intl';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
    PieChart, Pie, Cell, AreaChart, Area, ComposedChart, Line
} from 'recharts';
import { Truck, Calculator, Gavel, Users, TrendingUp, TrendingDown, Sparkles, AlertTriangle } from 'lucide-react';
import PriceForecast from './PriceForecast';

interface ForecastData {
    date: string;
    price_p10: number;
    price_p50: number;
    price_p90: number;
    is_extreme: boolean;
    reason?: string;
}

interface MandiDetailsProps {
    mandi: {
        mandi: string;
        net_profit: number;
        gross_value?: number;
        transport_cost: number;
        tax_amount?: number;
        labor_cost?: number;
        distance_km: number;
        vehicle?: string;
        price_per_qtl: number;
        retail_price?: number;
        trader_margin?: number;
    };
    forecast?: ForecastData[];
}

const COLORS = ['#ef4444', '#f59e0b', '#3b82f6']; // Red (Transport), Amber (Tax), Blue (Labor)

const MandiDetails: React.FC<MandiDetailsProps> = ({ mandi, forecast }) => {
    const t = useTranslations('MandiDetails');
    const locale = useLocale();

    // 1. Prepare Data for Bar Chart (Waterfall-ish: Revenue vs Cost vs Profit)
    const gross = mandi.gross_value || (mandi.price_per_qtl * 10); // fallback assumption if missing
    const tax = mandi.tax_amount || 0;
    const labor = mandi.labor_cost || 0;
    const transport = mandi.transport_cost;
    const totalCost = tax + labor + transport;

    const barData = [
        { name: t('financial.revenue'), value: gross, fill: '#10b981' }, // Green
        { name: t('financial.total_cost'), value: totalCost, fill: '#ef4444' }, // Red
        { name: t('financial.net_profit'), value: mandi.net_profit, fill: mandi.net_profit >= 0 ? '#3b82f6' : '#ef4444' }, // Blue if +, Red if -
    ];

    // 2. Prepare Data for Pie Chart (Cost Breakdown)
    const pieData = [
        { name: t('costs.transport'), value: transport },
        { name: t('costs.taxes'), value: tax },
        { name: t('costs.labor'), value: labor },
    ].filter(d => d.value > 0);

    // 3. Retail Price Analysis
    const retailPrice = mandi.retail_price || 0;
    const margin = mandi.trader_margin || 0;
    const marginPercent = retailPrice > 0 ? (margin / retailPrice) * 100 : 0;
    const isHighMargin = marginPercent > 50; // Arbitrary threshold for "High"

    // 4. Forecast Processing (Remaining data is now handled in PriceForecast component)

    return (
        <div className="flex flex-col gap-8 mt-6 w-full animate-fade-in">
            {/* AI FUTURE TREND DASHBOARD */}
            {forecast && forecast.length > 0 && (
                <PriceForecast forecast={forecast} />
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Cost Breakdown (Pie Chart & Details) */}
                <div className="eco-card p-6 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-amber-50 rounded-full blur-3xl -mr-16 -mt-16 transition-all duration-700 group-hover:bg-amber-100"></div>
                    <h4 className="font-semibold text-lg mb-4 flex items-center gap-2">
                        <Calculator size={20} className="text-amber-500" /> <span className="text-gray-800">{t('costs.title')}</span>
                    </h4>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center min-h-[280px]">
                        {/* Details List */}
                        <div className="space-y-4">
                            <div className="flex justify-between items-center p-3 bg-gray-50 hover:bg-gray-100 transition-colors rounded-lg border border-gray-100 shadow-sm">
                                <span className="text-gray-600 text-sm font-medium">{t('costs.transport')} ({mandi.vehicle || 'Unknown'})</span>
                                <span className="font-bold text-red-500">₹{transport.toLocaleString('en-IN', { maximumFractionDigits: 2 })}</span>
                            </div>
                            <div className="flex justify-between items-center p-3 bg-gray-50 hover:bg-gray-100 transition-colors rounded-lg border border-gray-100 shadow-sm">
                                <span className="text-gray-600 text-sm font-medium">{t('costs.taxes')}</span>
                                <span className="font-bold text-amber-500">₹{tax.toLocaleString('en-IN', { maximumFractionDigits: 2 })}</span>
                            </div>
                            <div className="flex justify-between items-center p-3 bg-gray-50 hover:bg-gray-100 transition-colors rounded-lg border border-gray-100 shadow-sm">
                                <span className="text-gray-600 text-sm font-medium">{t('costs.labor')}</span>
                                <span className="font-bold text-blue-500">₹{labor.toLocaleString('en-IN', { maximumFractionDigits: 2 })}</span>
                            </div>
                            <div className="flex justify-between items-center p-3 bg-gray-50 hover:bg-gray-100 transition-colors rounded-lg border border-gray-100 shadow-sm">
                                <span className="text-gray-600 text-sm font-medium">{t('costs.distance')}</span>
                                <span className="font-bold text-emerald-600">{mandi.distance_km} {t('costs.km')}</span>
                            </div>
                        </div>

                        {/* Cost Breakdown Visuals */}
                        <div className="h-full flex items-center justify-center relative min-h-[240px]">
                            {pieData.length > 0 ? (
                                <ResponsiveContainer width="100%" height="100%">
                                    <PieChart>
                                        <Pie
                                            data={pieData}
                                            cx="50%"
                                            cy="50%"
                                            innerRadius={60}
                                            outerRadius={90}
                                            paddingAngle={4}
                                            dataKey="value"
                                            stroke="none"
                                        >
                                            {pieData.map((entry, index) => (
                                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                            ))}
                                        </Pie>
                                        <Tooltip
                                            formatter={(value: any) => `₹${Number(value).toLocaleString('en-IN', { maximumFractionDigits: 2 })}`}
                                            contentStyle={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e5e7eb', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                            itemStyle={{ color: '#374151', fontWeight: 'bold' }}
                                        />
                                    </PieChart>
                                </ResponsiveContainer>
                            ) : (
                                <div className="text-gray-500 text-sm">No cost data available</div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Financial Overview (Bar Chart) */}
                <div className="eco-card p-6 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-50 rounded-full blur-3xl -mr-16 -mt-16 transition-all duration-700 group-hover:bg-emerald-100"></div>
                    <h4 className="font-semibold text-lg mb-4 flex items-center gap-2">
                        <Gavel size={20} className="text-emerald-500" /> <span className="text-gray-800">{t('financial.title')}</span>
                    </h4>
                    <div className="h-[280px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart
                                data={barData}
                                margin={{ top: 20, right: 10, left: 10, bottom: 5 }}
                                barSize={45}
                            >
                                <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" vertical={false} />
                                <XAxis
                                    dataKey="name"
                                    tick={{ fill: '#6b7280', fontSize: 13 }}
                                    axisLine={false}
                                    tickLine={false}
                                />
                                <YAxis
                                    tick={{ fill: '#6b7280', fontSize: 12 }}
                                    axisLine={false}
                                    tickLine={false}
                                    tickFormatter={(val) => `₹${val / 1000}k`}
                                    width={45}
                                />
                                <Tooltip
                                    cursor={{ fill: '#f3f4f6' }}
                                    contentStyle={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e5e7eb', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                    itemStyle={{ color: '#374151', fontWeight: 'bold' }}
                                    formatter={(value: any, name: any) => [`₹${Number(value).toLocaleString('en-IN', { maximumFractionDigits: 2 })}`, t('financial.amount')]}
                                />
                                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                                    {barData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.fill} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Bottom Section: Market Intelligence */}
            <div className="eco-card p-6 relative overflow-hidden mt-2">
                <div className="absolute inset-0 bg-purple-50 opacity-50"></div>
                <h4 className="font-semibold text-lg mb-6 flex items-center gap-2 relative z-10" style={{ color: 'var(--text-dark)' }}>
                    <Users size={20} className="text-purple-500" /> {t('intelligence.title')}
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative z-10">
                    <div className="p-5 bg-white rounded-xl border border-gray-100 shadow-sm relative z-10">
                        <p className="text-gray-500 text-sm mb-1 uppercase tracking-wider text-xs font-semibold">{t('intelligence.urban_retail')}</p>
                        <p className="text-3xl font-bold font-mono tracking-tight text-gray-800 mb-1">
                            {retailPrice > 0 ? `₹${retailPrice.toLocaleString('en-IN', { maximumFractionDigits: 2 })}` : <span className="text-gray-400 text-lg">{t('intelligence.na')}</span>}
                            <span className="text-sm font-sans text-gray-500 font-normal ml-1">{t('costs.per_qtl')}</span>
                        </p>
                        <p className="text-xs text-gray-400">{t('intelligence.consumer_pay')}</p>
                    </div>
                    <div className={`p-5 rounded-xl border shadow-sm relative z-10 ${isHighMargin ? 'border-red-200 bg-red-50' : 'border-emerald-200 bg-emerald-50'}`}>
                        <p className="text-gray-600 text-sm mb-1 uppercase tracking-wider text-xs font-semibold flex items-center gap-2">
                            {t('intelligence.middleman')}
                            {isHighMargin && <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>}
                        </p>
                        <p className={`text-3xl font-bold font-mono tracking-tight mb-1 ${retailPrice > 0 ? (isHighMargin ? 'text-red-500' : 'text-emerald-600') : 'text-gray-400'}`}>
                            {retailPrice > 0 ? `₹${margin.toLocaleString('en-IN', { maximumFractionDigits: 2 })}` : t('intelligence.na')}
                        </p>
                        <p className="text-xs text-gray-500">{t('intelligence.lost_value')}</p>
                    </div>
                    <div className="p-5 bg-white rounded-xl border border-gray-100 shadow-sm flex flex-col justify-center relative z-10">
                        <div className="flex justify-between items-end mb-2">
                            <p className="text-gray-500 text-sm uppercase tracking-wider text-xs font-semibold">{t('intelligence.farmer_share')}</p>
                            <p className="text-xl font-bold text-emerald-600">
                                {retailPrice > 0 ? `${(100 - marginPercent).toFixed(1)}%` : t('intelligence.na')}
                            </p>
                        </div>
                        <div className="w-full h-3 rounded-full overflow-hidden shadow-inner bg-gray-100 border border-gray-200">
                            <div
                                className="bg-gradient-to-r from-emerald-500 to-emerald-400 h-full rounded-r-full transition-all duration-1000"
                                style={{ width: `${retailPrice > 0 ? 100 - marginPercent : 0}%` }}
                            ></div>
                        </div>
                        <p className="text-xs text-gray-400 mt-2">{t('intelligence.keep_percent')}</p>
                    </div>
                </div>
            </div>
        </div >
    );
};

export default MandiDetails;
