"use client";

import React, { useEffect, useState } from 'react';
import { useLocale } from 'next-intl';
import { Users, Bell, Trash2, ShieldCheck, Download } from 'lucide-react';
import LanguageSwitcher from '@/components/LanguageSwitcher';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

interface UserData {
    name: string;
    phone: string;
    created_at: string;
}

interface RegistrationData {
    name: string;
    phone: string;
    commodity: string;
    mandi: string;
}

const AdminSkeleton = () => (
    <main className="p-8 max-w-7xl mx-auto space-y-8 animate-pulse">
        <section className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 min-h-[300px] w-full"></div>
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 min-h-[300px] w-full"></div>
        </section>
        <section>
            <div className="h-6 w-48 bg-gray-200 rounded-lg mb-4"></div>
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 min-h-[200px] w-full"></div>
        </section>
        <section>
            <div className="h-6 w-64 bg-gray-200 rounded-lg mb-4"></div>
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 min-h-[300px] w-full"></div>
        </section>
    </main>
);

export default function AdminPage() {
    const locale = useLocale();
    const router = useRouter();
    const { isAuthenticated } = useAuth();
    const [users, setUsers] = useState<UserData[]>([]);
    const [registrations, setRegistrations] = useState<RegistrationData[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!isAuthenticated) {
            router.push(`/${locale}/login`);
        }
    }, [isAuthenticated, router, locale]);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [uRes, rRes] = await Promise.all([
                    fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/admin/users`),
                    fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/admin/registrations`)
                ]);
                const uData = await uRes.json();
                const rData = await rRes.json();
                setUsers(uData);
                setRegistrations(rData);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const handleDeleteReg = async (phone: string, commodity: string) => {
        if (!confirm('Are you sure you want to delete this subscription?')) return;
        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/admin/registrations/${phone}?commodity=${commodity}`, {
                method: 'DELETE'
            });
            if (response.ok) {
                setRegistrations(registrations.filter(r => !(r.phone === phone && r.commodity === commodity)));
                toast.success('Subscription deleted');
            } else {
                toast.error('Failed to delete subscription');
            }
        } catch (err) {
            toast.error('Network error. Failed to delete');
        }
    };

    // Calculate Analytics Data
    const userGrowthData = React.useMemo(() => {
        const counts: Record<string, number> = {};
        users.forEach(u => {
            if (u.created_at) {
                const date = new Date(u.created_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' });
                counts[date] = (counts[date] || 0) + 1;
            }
        });
        return Object.entries(counts).map(([date, count]) => ({ date, count }));
    }, [users]);

    const commodityData = React.useMemo(() => {
        const counts: Record<string, number> = {};
        registrations.forEach(r => {
            counts[r.commodity] = (counts[r.commodity] || 0) + 1;
        });
        return Object.entries(counts).map(([name, value]) => ({ name, value }));
    }, [registrations]);

    const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#ef4444', '#14b8a6'];

    // CSV Exports
    const exportUsersCSV = () => {
        const headers = ["Name,Phone,Joined Date"];
        const rows = users.map(u => `"${u.name}","${u.phone}","${new Date(u.created_at).toLocaleDateString()}"`);
        const csv = headers.concat(rows).join("\n");
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'anshm_users.csv';
        a.click();
    };

    const exportRegsCSV = () => {
        const headers = ["Name,Commodity,Mandi,Phone"];
        const rows = registrations.map(r => `"${r.name}","${r.commodity}","${r.mandi}","${r.phone}"`);
        const csv = headers.concat(rows).join("\n");
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'anshm_subscriptions.csv';
        a.click();
    };

    if (!isAuthenticated) {
        return <div className="min-h-screen bg-gray-50 flex items-center justify-center"></div>;
    }

    return (
        <div className="min-h-screen bg-gray-50">
            <header className="bg-white border-b border-gray-200 px-8 py-4 flex items-center justify-between shadow-sm relative z-10">
                <div className="flex items-center gap-2 text-emerald-700 font-bold text-xl">
                    <ShieldCheck /> ANSH-M Admin Console
                </div>
                <div className="flex flex-col items-end">
                    <LanguageSwitcher />
                </div>
            </header>

            {loading ? <AdminSkeleton /> : (
            <main className="p-8 max-w-7xl mx-auto space-y-8">
                
                {/* Analytics Charts */}
                <section className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                        <h3 className="font-bold text-gray-800 mb-6 flex items-center gap-2">
                            <Users size={18} className="text-blue-500" /> User Registration Timeline
                        </h3>
                        <div className="h-64">
                            {userGrowthData.length > 0 ? (
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={userGrowthData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
                                        <XAxis dataKey="date" tick={{fontSize: 12, fill: '#6b7280'}} axisLine={false} tickLine={false} />
                                        <YAxis allowDecimals={false} tick={{fontSize: 12, fill: '#6b7280'}} axisLine={false} tickLine={false} />
                                        <Tooltip cursor={{fill: '#f9fafb'}} contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}} />
                                        <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} barSize={28} />
                                    </BarChart>
                                </ResponsiveContainer>
                            ) : (
                                <div className="h-full flex items-center justify-center text-gray-400 text-sm">No user data available</div>
                            )}
                        </div>
                    </div>
                    
                    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                        <h3 className="font-bold text-gray-800 mb-2 flex items-center gap-2">
                            <Bell size={18} className="text-emerald-500"/> Subscriptions by Commodity
                        </h3>
                        <div className="h-64">
                            {commodityData.length > 0 ? (
                                <ResponsiveContainer width="100%" height="100%">
                                    <PieChart>
                                        <Pie 
                                            data={commodityData} 
                                            dataKey="value" 
                                            nameKey="name" 
                                            cx="50%" 
                                            cy="50%" 
                                            innerRadius={60} 
                                            outerRadius={80} 
                                            paddingAngle={2}
                                            label={({name, percent}) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                                            labelLine={false}
                                        >
                                            {commodityData.map((entry, index) => (
                                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                            ))}
                                        </Pie>
                                        <Tooltip contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}} />
                                    </PieChart>
                                </ResponsiveContainer>
                            ) : (
                                <div className="h-full flex items-center justify-center text-gray-400 text-sm">No subscription data available</div>
                            )}
                        </div>
                    </div>
                </section>

                {/* Users Table */}
                <section>
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-2 text-gray-800 font-bold text-lg">
                            <Users size={20} className="text-blue-600" /> User Accounts ({users.length})
                        </div>
                        <button onClick={exportUsersCSV} className="flex items-center gap-2 text-sm text-gray-600 hover:text-blue-600 bg-white border border-gray-200 px-3 py-1.5 rounded-lg transition-colors hover:border-blue-200 hover:bg-blue-50 focus:outline-none">
                            <Download size={14}/> Export CSV
                        </button>
                    </div>
                    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                        <table className="w-full text-left">
                            <thead className="bg-gray-50 text-gray-500 text-xs uppercase tracking-wider">
                                <tr>
                                    <th className="px-6 py-4">Name</th>
                                    <th className="px-6 py-4">Phone</th>
                                    <th className="px-6 py-4">Joined</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100 text-sm">
                                {users.length > 0 ? users.map((u, i) => (
                                    <tr key={i} className="hover:bg-gray-50/50 transition-colors">
                                        <td className="px-6 py-4 font-medium text-gray-900">{u.name}</td>
                                        <td className="px-6 py-4 text-gray-600 font-mono">{u.phone}</td>
                                        <td className="px-6 py-4 text-gray-400">{new Date(u.created_at).toLocaleDateString()}</td>
                                    </tr>
                                )) : (
                                    <tr>
                                        <td colSpan={3} className="px-6 py-8 text-center text-gray-500">No users found.</td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </section>

                {/* Registrations Table */}
                <section>
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-2 text-gray-800 font-bold text-lg">
                            <Bell size={20} className="text-emerald-600" /> Active Alert Subscriptions ({registrations.length})
                        </div>
                        <button onClick={exportRegsCSV} className="flex items-center gap-2 text-sm text-gray-600 hover:text-emerald-600 bg-white border border-gray-200 px-3 py-1.5 rounded-lg transition-colors hover:border-emerald-200 hover:bg-emerald-50 focus:outline-none">
                            <Download size={14}/> Export CSV
                        </button>
                    </div>
                    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                        <table className="w-full text-left">
                            <thead className="bg-gray-50 text-gray-500 text-xs uppercase tracking-wider">
                                <tr>
                                    <th className="px-6 py-4">User</th>
                                    <th className="px-6 py-4">Commodity</th>
                                    <th className="px-6 py-4">Mandi</th>
                                    <th className="px-6 py-4">Phone</th>
                                    <th className="px-6 py-4 text-right">Action</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100 text-sm">
                                {registrations.length > 0 ? registrations.map((r, i) => (
                                    <tr key={i} className="hover:bg-gray-50/50 transition-colors">
                                        <td className="px-6 py-4 font-medium text-gray-900">{r.name}</td>
                                        <td className="px-6 py-4 text-gray-600"><span className="bg-emerald-50 text-emerald-700 px-2.5 py-1 rounded-full text-xs font-bold">{r.commodity}</span></td>
                                        <td className="px-6 py-4 text-gray-600">{r.mandi}</td>
                                        <td className="px-6 py-4 text-gray-400 font-mono">{r.phone}</td>
                                        <td className="px-6 py-4 text-right">
                                            <button onClick={() => handleDeleteReg(r.phone, r.commodity)} className="text-red-400 hover:text-red-600 transition-colors p-2 hover:bg-red-50 rounded-lg focus:outline-none">
                                                <Trash2 size={16} />
                                            </button>
                                        </td>
                                    </tr>
                                )) : (
                                    <tr>
                                        <td colSpan={5} className="px-6 py-8 text-center text-gray-500">No alert subscriptions found.</td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </section>
            </main>
            )}
        </div>
    );
}
