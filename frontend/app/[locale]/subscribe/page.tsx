"use client";

import React, { useState, useEffect } from 'react';
import { useLocale } from 'next-intl';
import { Smartphone, User, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';
import MandiFinder, { MandiOption } from '@/components/MandiFinder';
import toast from 'react-hot-toast';

export default function SubscribePage() {
    const locale = useLocale();
    const router = useRouter();
    const { user, isAuthenticated } = useAuth();
    const [selectedMandi, setSelectedMandi] = useState<MandiOption | null>(null);
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);

    useEffect(() => {
        if (!isAuthenticated) {
            router.push(`/${locale}/login`);
        }
    }, [isAuthenticated, router, locale]);

    if (!isAuthenticated) return <div className="min-h-screen bg-gray-50 flex items-center justify-center">Loading...</div>;

    const handleSubscribe = async () => {
        if (!selectedMandi || !selectedMandi.state || !selectedMandi.mandi || !selectedMandi.commodity) {
            toast.error("Please select a location and crop first by clicking 'Find Best Price'.");
            return;
        }

        setLoading(true);
        try {
            const payload = {
                name: user?.name || "User",
                phone: user?.phone || "",
                commodity: selectedMandi.commodity,
                state: selectedMandi.state,
                mandi: selectedMandi.mandi
            };

            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/alerts/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                toast.success('Successfully activated SMS Alerts!');
                setSuccess(true);
            } else {
                const err = await res.json();
                toast.error(err.detail || 'Subscription failed');
            }
        } catch (err) {
            toast.error('Server connection error');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#fdfcf9] py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-3xl mx-auto space-y-8">
                <div className="text-center">
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">Daily SMS Alerts 📱</h1>
                    <p className="text-gray-500">Get morning AI price forecasts directly to your phone.</p>
                </div>

                {success ? (
                    <div className="bg-emerald-50 border border-emerald-200 rounded-3xl p-8 text-center animate-fade-in shadow-sm">
                        <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4">
                            <CheckCircle2 className="text-emerald-600" size={32} />
                        </div>
                        <h2 className="text-2xl font-bold text-emerald-800 mb-2">Subscribed Successfully!</h2>
                        <p className="text-emerald-700 mb-6">You will receive your first SMS alert shortly for {selectedMandi?.commodity} at {selectedMandi?.mandi}.</p>
                        <button 
                            onClick={() => router.push(`/${locale}`)}
                            className="px-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-2xl shadow-lg transition-all"
                        >
                            Return to Dashboard
                        </button>
                    </div>
                ) : (
                    <div className="bg-white rounded-3xl shadow-xl border border-emerald-50 overflow-hidden">
                        <div className="p-8 border-b border-gray-100">
                            <h2 className="text-xl font-bold text-gray-800 mb-6">1. Select Location & Crop</h2>
                            <div className="bg-gray-50 rounded-2xl p-4 border border-gray-100">
                                <MandiFinder onSelectMandi={setSelectedMandi} />
                            </div>
                        </div>

                        <div className="p-8">
                            <h2 className="text-xl font-bold text-gray-800 mb-6">2. Confirm Details</h2>

                            <div className="space-y-4 mb-8">
                                <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-xl border border-gray-100">
                                    <User className="text-gray-400" size={20} />
                                    <div>
                                        <p className="text-xs font-bold text-gray-500 uppercase tracking-wider">Subscriber Name</p>
                                        <p className="font-semibold text-gray-900">{user?.name || "Loading..."}</p>
                                    </div>
                                </div>
                                <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-xl border border-gray-100">
                                    <Smartphone className="text-gray-400" size={20} />
                                    <div>
                                        <p className="text-xs font-bold text-gray-500 uppercase tracking-wider">Phone Number</p>
                                        <p className="font-semibold text-gray-900">{user?.phone || "Loading..."}</p>
                                    </div>
                                </div>
                            </div>

                            <button
                                onClick={handleSubscribe}
                                disabled={loading || !selectedMandi}
                                className={`w-full py-4 font-bold rounded-2xl shadow-lg transition-all flex items-center justify-center gap-2 ${
                                    loading || !selectedMandi 
                                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed shadow-none' 
                                    : 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-emerald-200'
                                }`}
                            >
                                {loading ? <Loader2 className="animate-spin" size={20} /> : <Smartphone size={20} />}
                                {loading ? 'Activating...' : 'Activate SMS Alerts'}
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
