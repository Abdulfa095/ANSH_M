"use client";

import React, { useState } from 'react';
import { useLocale } from 'next-intl';
import { Smartphone, User, Lock, Loader2, UserPlus } from 'lucide-react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import toast from 'react-hot-toast';

export default function RegisterPage() {
    const locale = useLocale();
    const router = useRouter();
    const [formData, setFormData] = useState({ name: '', phone: '', password: '' });
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            const formattedPhone = formData.phone.startsWith('+91') ? formData.phone : `+91${formData.phone.replace(/^0+/, '')}`;
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/auth/signup`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: formData.name, phone: formattedPhone, password: formData.password })
            });

            if (res.ok) {
                toast.success('Account created successfully!');
                router.push(`/${locale}/login`);
            } else {
                const err = await res.json();
                toast.error(err.detail || 'Registration failed');
            }
        } catch (err) {
            toast.error('Server connection error');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-[#fdfcf9]">
            <div className="w-full max-w-md p-8 bg-white rounded-3xl shadow-xl border border-emerald-50">
                <div className="text-center mb-10">
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">Join ANSH-M</h1>
                    <p className="text-gray-500">Start your smart farming journey today</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-5">
                    
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-1.5">Full Name</label>
                        <div className="relative">
                            <User className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                            <input
                                type="text"
                                required
                                value={formData.name}
                                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-100 rounded-2xl focus:ring-2 focus:ring-emerald-500 outline-none transition-all"
                                placeholder="Your Name"
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-1.5">Phone Number</label>
                        <div className="relative">
                            <Smartphone className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                            <input
                                type="tel"
                                required
                                value={formData.phone}
                                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                                className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-100 rounded-2xl focus:ring-2 focus:ring-emerald-500 outline-none transition-all"
                                placeholder="9876543210"
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-1.5">Password</label>
                        <div className="relative">
                            <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                            <input
                                type="password"
                                required
                                value={formData.password}
                                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-100 rounded-2xl focus:ring-2 focus:ring-emerald-500 outline-none transition-all"
                                placeholder="Create a password"
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full py-4 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-2xl shadow-lg shadow-emerald-200 transition-all flex items-center justify-center gap-2 mt-4"
                    >
                        {loading ? <Loader2 className="animate-spin" /> : <UserPlus size={20} />}
                        Create Account
                    </button>
                </form>

                <p className="mt-8 text-center text-gray-500 text-sm">
                    Already have an account?{' '}
                    <Link href={`/${locale}/login`} className="text-emerald-600 font-bold hover:underline">
                        Log in here
                    </Link>
                </p>
            </div>
        </div>
    );
}
