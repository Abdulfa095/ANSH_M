"use client";

import React, { useState, useRef, useEffect } from 'react';
import { useTranslations, useLocale } from 'next-intl';
import { Search, MapPin, Truck, DollarSign, Navigation, CalendarDays } from 'lucide-react';
import MandiDetails from './MandiDetails';
import { TN_TALUKS, TN_DISTRICT_COORDS } from './TNTaluks';
import { ChevronDown } from 'lucide-react';

// Custom Select Component to prevent full-screen native dropdowns
interface CustomSelectProps {
    value: string;
    options: { label: string, value: string }[];
    onChange: (val: string) => void;
    placeholder: string;
    disabled?: boolean;
}

const CustomSelect: React.FC<CustomSelectProps> = ({ value, options, onChange, placeholder, disabled }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [focusedIndex, setFocusedIndex] = useState(-1);
    const containerRef = useRef<HTMLDivElement>(null);
    const listboxRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };

        if (isOpen) {
            document.addEventListener('mousedown', handleClickOutside);
            const index = options.findIndex(o => o.value === value);
            setFocusedIndex(index >= 0 ? index : 0);
        }

        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [isOpen, value, options]);

    useEffect(() => {
        if (isOpen && focusedIndex >= 0 && listboxRef.current) {
            const focusedEl = listboxRef.current.children[focusedIndex + (placeholder ? 1 : 0)] as HTMLElement;
            if (focusedEl) {
                focusedEl.scrollIntoView({ block: 'nearest' });
            }
        }
    }, [focusedIndex, isOpen, placeholder]);

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (disabled) return;
        
        switch (e.key) {
            case 'Enter':
            case ' ':
                e.preventDefault();
                if (isOpen && focusedIndex >= 0 && focusedIndex < options.length) {
                    onChange(options[focusedIndex].value);
                    setIsOpen(false);
                } else if (!isOpen) {
                    setIsOpen(true);
                }
                break;
            case 'Escape':
                setIsOpen(false);
                break;
            case 'ArrowDown':
                e.preventDefault();
                if (!isOpen) {
                    setIsOpen(true);
                } else {
                    setFocusedIndex(prev => (prev < options.length - 1 ? prev + 1 : prev));
                }
                break;
            case 'ArrowUp':
                e.preventDefault();
                if (isOpen) {
                    setFocusedIndex(prev => (prev > 0 ? prev - 1 : 0));
                }
                break;
            case 'Tab':
                if (isOpen) setIsOpen(false);
                break;
        }
    };

    return (
        <div 
            className="relative w-full" 
            ref={containerRef}
            onKeyDown={handleKeyDown}
        >
            <button
                type="button"
                aria-haspopup="listbox"
                aria-expanded={isOpen}
                aria-disabled={disabled}
                style={{
                    background: disabled ? '#f3f4f6' : '#fff',
                    border: `1.5px solid ${disabled ? '#e5e7eb' : isOpen ? 'var(--green-brand)' : 'var(--card-border)'}`,
                    color: disabled ? '#9ca3af' : 'var(--text-dark)',
                    opacity: disabled ? 0.6 : 1,
                    cursor: disabled ? 'not-allowed' : 'pointer',
                    outline: 'none',
                    boxShadow: isOpen ? '0 0 0 3px rgba(34,164,71,0.12)' : 'none'
                }}
                className="w-full flex items-center justify-between rounded-lg h-11 px-3 transition-all hover:border-green-500 focus-visible:ring-2 focus-visible:ring-green-500"
                onClick={() => !disabled && setIsOpen(!isOpen)}
            >
                <span className="text-sm">
                    {options.find(o => o.value === value)?.label || <span className="text-gray-400">{placeholder}</span>}
                </span>
                <ChevronDown size={16} style={{ color: 'var(--text-muted)' }} className={`transition-transform ${isOpen ? 'rotate-180' : ''}`} />
            </button>

            {isOpen && !disabled && (
                <div 
                    ref={listboxRef}
                    role="listbox"
                    className="absolute z-[100] top-full mt-1 w-full rounded-xl shadow-2xl max-h-60 overflow-y-auto custom-scrollbar" 
                    style={{ background: '#fff', border: '1.5px solid var(--card-border)' }}
                >
                    {placeholder && (
                        <div
                            className="px-4 py-2.5 text-sm cursor-pointer border-b opacity-70"
                            style={{ color: 'var(--text-muted)', borderColor: 'var(--card-border)' }}
                            onClick={() => { onChange(""); setIsOpen(false); }}
                        >
                            {placeholder}
                        </div>
                    )}
                    {options.map((opt, i) => (
                        <div
                            key={i}
                            role="option"
                            aria-selected={value === opt.value}
                            className={`px-4 py-2.5 text-sm cursor-pointer transition-colors ${focusedIndex === i ? 'bg-green-50' : ''}`}
                            style={{
                                color: value === opt.value ? 'var(--green-brand)' : 'var(--text-dark)',
                                background: (value === opt.value || focusedIndex === i) ? 'var(--cream-dark)' : 'transparent',
                            }}
                            onMouseEnter={() => setFocusedIndex(i)}
                            onClick={() => { onChange(opt.value); setIsOpen(false); }}
                        >
                            {opt.label}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

// ─── Locale-aware Date Picker ─────────────────────────────────────────────────
const MONTH_NAMES_TA = [
    'ஜனவரி','பிப்ரவரி','மார்ச்','ஏப்ரல்','மே','ஜூன்',
    'ஜூலை','ஆகஸ்ட்','செப்டம்பர்','அக்டோபர்','நவம்பர்','டிசம்பர்'
];
const MONTH_NAMES_EN = [
    'January','February','March','April','May','June',
    'July','August','September','October','November','December'
];
const DAY_NAMES_TA = ['ஞா','திங்','செவ்','புத','வியா','வெள்','சனி'];
const DAY_NAMES_EN = ['Su','Mo','Tu','We','Th','Fr','Sa'];

interface CustomDatePickerProps {
    value: string; // YYYY-MM-DD
    onChange: (val: string) => void;
    max?: string;
    placeholder?: string;
}

const CustomDatePicker: React.FC<CustomDatePickerProps> = ({ value, onChange, max, placeholder }) => {
    const locale = useLocale();
    const isTamil = locale === 'ta';
    const MONTHS = isTamil ? MONTH_NAMES_TA : MONTH_NAMES_EN;
    const DAYS = isTamil ? DAY_NAMES_TA : DAY_NAMES_EN;

    const today = new Date();
    const initDate = value ? new Date(value) : today;
    const [viewYear, setViewYear] = useState(initDate.getFullYear());
    const [viewMonth, setViewMonth] = useState(initDate.getMonth());
    const [open, setOpen] = useState(false);
    const ref = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handler = (e: MouseEvent) => {
            if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
        };
        document.addEventListener('mousedown', handler);
        return () => document.removeEventListener('mousedown', handler);
    }, []);

    const maxDate = max ? new Date(max) : today;

    const firstDay = new Date(viewYear, viewMonth, 1).getDay();
    const daysInMonth = new Date(viewYear, viewMonth + 1, 0).getDate();

    const selectDay = (day: number) => {
        const d = `${viewYear}-${String(viewMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        if (new Date(d) <= maxDate) { onChange(d); setOpen(false); }
    };

    const prevMonth = () => viewMonth === 0 ? (setViewYear(y => y - 1), setViewMonth(11)) : setViewMonth(m => m - 1);
    const nextMonth = () => {
        const nextM = viewMonth === 11 ? 0 : viewMonth + 1;
        const nextY = viewMonth === 11 ? viewYear + 1 : viewYear;
        if (new Date(nextY, nextM, 1) <= maxDate) { setViewYear(nextY); setViewMonth(nextM); }
    };

    const displayLabel = value
        ? isTamil
            ? `${new Date(value).getDate()} ${MONTHS[new Date(value).getMonth()]} ${new Date(value).getFullYear()}`
            : new Date(value).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
        : placeholder || (isTamil ? 'தேதி தேர்வு' : 'Select date');

    return (
        <div ref={ref} className="relative w-full">
            <button
                type="button"
                onClick={() => setOpen(o => !o)}
                className="w-full flex items-center gap-2 rounded-lg h-11 px-3 text-sm transition-all hover:border-green-500 overflow-hidden"
                style={{ background: '#fff', border: '1.5px solid var(--card-border)', color: value ? 'var(--text-dark)' : '#9ca3af' }}
            >
                <CalendarDays size={15} style={{ color: 'var(--green-brand)', flexShrink: 0 }} />
                <span className="truncate flex-1 text-left">{displayLabel}</span>
            </button>
            {open && (
                <div className="absolute z-[200] top-full mt-1 rounded-xl shadow-2xl p-3 w-64"
                    style={{ background: '#fff', border: '1.5px solid var(--card-border)', minWidth: '220px' }}>
                    {/* Month/Year nav */}
                    <div className="flex items-center justify-between mb-2">
                        <button onClick={prevMonth} className="px-2 py-1 rounded hover:bg-green-50 font-bold" type="button">‹</button>
                        <span className="text-xs font-bold" style={{ color: 'var(--text-dark)' }}>
                            {MONTHS[viewMonth]} {viewYear}
                        </span>
                        <button onClick={nextMonth} className="px-2 py-1 rounded hover:bg-green-50 font-bold" type="button">›</button>
                    </div>
                    {/* Day headers */}
                    <div className="grid grid-cols-7 mb-1">
                        {DAYS.map(d => (
                            <div key={d} className="text-center text-xs font-semibold py-1" style={{ color: 'var(--text-muted)' }}>{d}</div>
                        ))}
                    </div>
                    {/* Day cells */}
                    <div className="grid grid-cols-7 gap-y-0.5">
                        {Array.from({ length: firstDay }).map((_, i) => <div key={`e${i}`} />)}
                        {Array.from({ length: daysInMonth }, (_, i) => i + 1).map(day => {
                            const iso = `${viewYear}-${String(viewMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
                            const isSelected = value === iso;
                            const isDisabled = new Date(iso) > maxDate;
                            const isToday = iso === today.toISOString().split('T')[0];
                            return (
                                <button
                                    key={day}
                                    type="button"
                                    disabled={isDisabled}
                                    onClick={() => selectDay(day)}
                                    className="text-xs rounded-lg h-7 w-full transition-all"
                                    style={{
                                        background: isSelected ? 'var(--green-brand)' : isToday ? 'var(--cream-dark)' : 'transparent',
                                        color: isSelected ? '#fff' : isDisabled ? '#d1d5db' : 'var(--text-dark)',
                                        fontWeight: isSelected || isToday ? 'bold' : 'normal',
                                        cursor: isDisabled ? 'not-allowed' : 'pointer',
                                    }}
                                >{day}</button>
                            );
                        })}
                    </div>
                    {value && (
                        <button type="button" onClick={() => { onChange(''); setOpen(false); }}
                            className="mt-2 w-full text-xs py-1 rounded-lg"
                            style={{ color: 'var(--text-muted)', background: 'var(--cream-dark)' }}>
                            {isTamil ? 'அழி' : 'Clear'}
                        </button>
                    )}
                </div>
            )}
        </div>
    );
};

import dynamic from 'next/dynamic';

const MandiMap = dynamic(() => import('./MandiMap'), {
    ssr: false,
    loading: () => <div className="h-[400px] w-full bg-white/5 rounded-xl animate-pulse flex items-center justify-center text-gray-500">Loading Map...</div>
});

export interface MandiOption {
    mandi: string;
    translated_name?: string;
    variety?: string;
    net_profit: number;
    gross_value?: number;
    distance_km: number;
    transport_cost: number;
    tax_amount?: number;
    labor_cost?: number;
    vehicle?: string;
    price_per_qtl: number;
    retail_price?: number;
    trader_margin?: number;
    lat: number;
    lon: number;
    commodity?: string;
    state?: string;
    is_predicted?: boolean;
    last_updated?: string;
    search_date?: string;
}
// ... (State Districts remain same) ...



// State → District mapping with coordinates
const STATE_DISTRICTS: Record<string, Record<string, any>> = {
    "Tamil Nadu": TN_TALUKS, // We replaced the simple dict with the deeply nested Taluk map
    "Maharashtra": {
        "Nashik": { lat: 19.9975, lon: 73.7898 },
        "Pune": { lat: 18.5204, lon: 73.8567 },
        "Mumbai": { lat: 19.0760, lon: 72.8777 },
        "Nagpur": { lat: 21.1458, lon: 79.0882 },
        "Aurangabad": { lat: 19.8762, lon: 75.3433 },
        "Solapur": { lat: 17.6599, lon: 75.9064 },
        "Kolhapur": { lat: 16.7050, lon: 74.2433 },
        "Sangli": { lat: 16.8524, lon: 74.5815 },
    },
    "Andhra Pradesh": {
        "Kurnool": { lat: 15.8281, lon: 78.0373 },
        "Vijayawada": { lat: 16.5062, lon: 80.6480 },
        "Visakhapatnam": { lat: 17.6868, lon: 83.2185 },
        "Guntur": { lat: 16.3067, lon: 80.4365 },
        "Tirupati": { lat: 13.6288, lon: 79.4192 },
        "Anantapur": { lat: 14.6819, lon: 77.6006 },
    },
    "Karnataka": {
        "Bengaluru": { lat: 12.9716, lon: 77.5946 },
        "Mysuru": { lat: 12.2958, lon: 76.6394 },
        "Hubli": { lat: 15.3647, lon: 75.1240 },
        "Mangaluru": { lat: 12.9141, lon: 74.8560 },
        "Belgaum": { lat: 15.8497, lon: 74.4977 },
    },
    "Punjab": {
        "Ludhiana": { lat: 30.9010, lon: 75.8573 },
        "Amritsar": { lat: 31.6340, lon: 74.8723 },
        "Jalandhar": { lat: 31.3260, lon: 75.5762 },
        "Khanna": { lat: 30.7070, lon: 76.2160 },
        "Patiala": { lat: 30.3398, lon: 76.3869 },
    },
    "Uttar Pradesh": {
        "Lucknow": { lat: 26.8467, lon: 80.9462 },
        "Agra": { lat: 27.1767, lon: 78.0081 },
        "Varanasi": { lat: 25.3176, lon: 82.9739 },
        "Kanpur": { lat: 26.4499, lon: 80.3319 },
        "Allahabad": { lat: 25.4358, lon: 81.8463 },
    },
    "Madhya Pradesh": {
        "Indore": { lat: 22.7196, lon: 75.8577 },
        "Bhopal": { lat: 23.2599, lon: 77.4126 },
        "Jabalpur": { lat: 23.1815, lon: 79.9864 },
        "Gwalior": { lat: 26.2183, lon: 78.1828 },
    },
    "Rajasthan": {
        "Jaipur": { lat: 26.9124, lon: 75.7873 },
        "Jodhpur": { lat: 26.2389, lon: 73.0243 },
        "Kota": { lat: 25.2138, lon: 75.8648 },
        "Udaipur": { lat: 24.5854, lon: 73.7125 },
    },
    "Telangana": {
        "Hyderabad": { lat: 17.3850, lon: 78.4867 },
        "Warangal": { lat: 17.9784, lon: 79.5941 },
        "Karimnagar": { lat: 18.4386, lon: 79.1288 },
        "Nizamabad": { lat: 18.6725, lon: 78.0940 },
    },
    "Gujarat": {
        "Ahmedabad": { lat: 23.0225, lon: 72.5714 },
        "Surat": { lat: 21.1702, lon: 72.8311 },
        "Rajkot": { lat: 22.3039, lon: 70.8022 },
        "Vadodara": { lat: 22.3072, lon: 73.1812 },
    },
};

const COMMODITIES = ["Onion", "Tomato", "Potato", "Rice", "Wheat"];

const COMMODITY_VARIETIES: Record<string, string[]> = {
    "Onion": ["Red", "White", "Bellari", "Local", "Nasik", "Pusa Red"],
    "Tomato": ["Local", "Hybrid", "Deshi", "Apple"],
    "Potato": ["Local", "Jyoti", "Deshi", "Chandramukhi", "Hassan"],
    "Rice": ["Common", "Fine", "Super Fine", "IR-64", "Sona Masuri", "Basmati", "Ponni"],
    "Wheat": ["Common", "Deshi", "Sharbati", "Lokwan", "Mill Quality"]
};

interface MandiFinderProps {
    onSelectMandi?: (mandi: MandiOption | null) => void;
}

const MandiFinder: React.FC<MandiFinderProps> = ({ onSelectMandi }) => {
    const t = useTranslations('MandiFinder');
    const locale = useLocale();
    const [quantity, setQuantity] = useState(10);
    const [results, setResults] = useState<MandiOption[]>([]);
    const [loading, setLoading] = useState(false);
    const [hasSearched, setHasSearched] = useState(false);
    const [location, setLocation] = useState<{ lat: number, lon: number } | null>(null);
    const [locStatus, setLocStatus] = useState("");
    const [selectedState, setSelectedState] = useState("Tamil Nadu");
    const [selectedDistrict, setSelectedDistrict] = useState("");
    const [selectedTaluk, setSelectedTaluk] = useState("");
    const [selectedCommodity, setSelectedCommodity] = useState("Onion");
    const [selectedVariety, setSelectedVariety] = useState("");
    const [selectedDate, setSelectedDate] = useState("");
    const [expandedMandi, setExpandedMandi] = useState<string | null>(null);

    // Reset variety when commodity changes
    useEffect(() => {
        setSelectedVariety("");
    }, [selectedCommodity]);

    const toggleExpand = (mandiObj: MandiOption) => {
        const isCurrentlyExpanded = expandedMandi === mandiObj.mandi;
        setExpandedMandi(isCurrentlyExpanded ? null : mandiObj.mandi);
        if (onSelectMandi) {
            onSelectMandi(isCurrentlyExpanded ? null : mandiObj);
        }
    }

    const handleStateChange = (state: string) => {
        setSelectedState(state);
        setSelectedDistrict("");
        setSelectedTaluk("");
        setLocation(null);
        setLocStatus("");
    };

    const handleDistrictChange = (district: string) => {
        setSelectedDistrict(district);
        setSelectedTaluk("");

        // If it's NOT Tamil Nadu, use district directly for cords
        if (selectedState && selectedState !== "Tamil Nadu" && STATE_DISTRICTS[selectedState]?.[district]) {
            const coords = (STATE_DISTRICTS as any)[selectedState][district];
            setLocation({ lat: coords.lat, lon: coords.lon });
            setLocStatus(`📍 ${district}, ${selectedState}`);
        } else {
            setLocation(null);
            setLocStatus("");
        }
    };

    const handleTalukChange = (taluk: string) => {
        console.log("DEBUG: handleTalukChange called with:", taluk);
        setSelectedTaluk(taluk);
        if (taluk && selectedState === "Tamil Nadu" && selectedDistrict) {
            // Find the key in TN_TALUKS that matches the selected taluk
            const taluksObj = TN_TALUKS[selectedDistrict] || {};
            const talukKey = Object.keys(taluksObj).find(k => k === taluk);

            const talukCoords = talukKey ? taluksObj[talukKey] : null;

            console.log("DEBUG: Resolved talukKey:", talukKey, "talukCoords:", talukCoords);

            // Use taluk-specific coords only if they are NOT the generic placeholder (10.82, 78.68)
            const isPlaceholder = talukCoords?.lat === 10.82 && talukCoords?.lon === 78.68;
            const coords = (!isPlaceholder && talukCoords)
                ? talukCoords
                : TN_DISTRICT_COORDS[selectedDistrict];

            console.log("DEBUG: Final coordinates chosen:", coords, "Is placeholder?", isPlaceholder);

            if (coords) {
                setLocation({ lat: coords.lat, lon: coords.lon });
                setLocStatus(`📍 ${taluk}, ${selectedDistrict}, TN (${coords.lat.toFixed(4)}, ${coords.lon.toFixed(4)})`);
            }
        }
    };

    const handleLiveLocation = () => {
        if ("geolocation" in navigator) {
            setLocStatus("Fetching GPS...");
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    setLocation({
                        lat: position.coords.latitude,
                        lon: position.coords.longitude
                    });
                    setLocStatus("📍 Live GPS Active");
                    setSelectedState("GPS Enabled");
                    setSelectedDistrict("Auto");
                },
                (error) => {
                    console.error("Error getting location", error);
                    setLocStatus("GPS Blocked. Use dropdowns.");
                }
            );
        } else {
            alert("Geolocation is not supported by your browser");
        }
    };

    const handleSearch = async () => {
        if (!location || !selectedState) {
            alert("Please select a State and District first!");
            return;
        }

        setLoading(true);
        setHasSearched(true);
        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/mandi/suggest`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    farmer_lat: location.lat,
                    farmer_lon: location.lon,
                    commodity: selectedCommodity,
                    variety: selectedVariety,
                    date: selectedDate || undefined,
                    quantity_quintals: quantity,
                    state: selectedState
                })
            });
            const data = await response.json();
            console.log("DEBUG: API Response Data:", data);

            if (!data || data.length === 0) {
                console.warn("DEBUG: No live data returned from API");
                setResults([]);
                return;
            }

            const formattedResults = data.map((item: any) => ({
                mandi: item.mandi,
                translated_name: getMandiLabel(item.mandi),
                net_profit: item.net_profit,
                gross_value: item.gross_value,
                distance_km: item.distance_km,
                transport_cost: item.transport_cost,
                tax_amount: item.tax_amount,
                labor_cost: item.labor_cost,
                vehicle: item.vehicle,
                price_per_qtl: item.price_per_qtl,
                lat: item.lat || 0,
                lon: item.lon || 0,
                retail_price: item.retail_price,
                trader_margin: item.trader_margin,
                price: item.price_per_qtl,
                profit: item.net_profit,
                commodity: selectedCommodity,
                variety: selectedVariety,
                state: selectedState,
                is_predicted: item.is_predicted,
                last_updated: item.last_updated,
                search_date: selectedDate || undefined
            }));
            setResults(formattedResults);
        } catch (error) {
            console.error("Error finding mandis", error);
        } finally {
            setLoading(false);
        }
    };

    const districts = selectedState ? Object.keys(STATE_DISTRICTS[selectedState] || {}).sort() : [];

    const getDistrictLabel = (d: string) => { const k = d.replace(/ /g, '_').replace(/\./g, ''); return t.has(`districts.${k}` as any) ? t(`districts.${k}` as any) : d; };
    const getTalukLabel = (ta: string) => { const k = ta.replace(/ /g, '_').replace(/\./g, ''); return t.has(`taluks.${k}` as any) ? t(`taluks.${k}` as any) : ta; };
    const getCommodityLabel = (c: string) => { const k = c.replace(/ /g, '_').replace(/\./g, ''); return t.has(`commodities.${k}` as any) ? t(`commodities.${k}` as any) : c; };
    const getVarietyLabel = (v: string) => { const k = v.replace(/ /g, '_').replace(/\./g, ''); return t.has(`varieties.${k}` as any) ? t(`varieties.${k}` as any) : v; };
    const getMandiLabel = (m: string) => {
        // 1. Direct dictionary match
        const k = m.replace(/[^a-zA-Z0-9]+/g, '_').replace(/^_|_$/g, '');
        if (t.has(`mandis.${k}` as any)) return t(`mandis.${k}` as any);

        // 2. Dynamic matching for Tamil Nadu APMC patterns
        if (locale !== 'ta') return m;

        let prefix = m;
        let suffix = "";

        if (m.toLowerCase().includes('uzhavar')) {
            prefix = m.split(/\s*\(?uzhavar/i)[0].trim();
            suffix = " (உழவர் சந்தை) APMC";
        } else if (m.toLowerCase().endsWith('apmc')) {
            prefix = m.replace(/\s*apmc$/i, '').trim();
            suffix = " APMC";
        }

        prefix = prefix.replace(/[\(\)]/g, '').trim();
        const prefixKey = prefix.replace(/ /g, '_').replace(/\./g, '');

        if (t.has(`mandis.${prefixKey}` as any)) {
            return t(`mandis.${prefixKey}` as any) + suffix;
        } else if (t.has(`taluks.${prefixKey}` as any)) {
            return t(`taluks.${prefixKey}` as any) + suffix;
        } else if (t.has(`districts.${prefixKey}` as any)) {
            return t(`districts.${prefixKey}` as any) + suffix;
        }

        return m;
    };

    return (
        <div className="eco-card p-6 space-y-5">
            <h2 className="text-lg font-bold flex items-center gap-2" style={{ color: 'var(--text-dark)' }}>
                <MapPin style={{ color: 'var(--green-brand)' }} size={20} /> {t('title')}
            </h2>

            <div className="flex flex-col gap-4">
                <button
                    onClick={handleLiveLocation}
                    className="w-full btn-outline-green flex items-center justify-center gap-2 py-2.5 text-sm"
                >
                    <Navigation size={16} /> {t('live_gps')}
                </button>

                <div className="flex items-center gap-2">
                    <div className="h-px flex-1" style={{ background: 'var(--card-border)' }} />
                    <span className="text-xs font-semibold uppercase tracking-widest" style={{ color: 'var(--text-muted)' }}>{t('or_select')}</span>
                    <div className="h-px flex-1" style={{ background: 'var(--card-border)' }} />
                </div>

                {/* State, District & Taluk Selectors */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label className="block text-xs font-semibold mb-1.5 label-tag">{t('state')}</label>
                        <CustomSelect
                            value={selectedState}
                            onChange={handleStateChange}
                            placeholder={t('select_state')}
                            options={[
                                ...(selectedState === "GPS Enabled" ? [{ label: `📍 ${t('states.GPS_Enabled')}`, value: "GPS Enabled" }] : []),
                                ...Object.keys(STATE_DISTRICTS).sort().map(state => ({ 
                                    label: t.has(`states.${state.replace(/ /g, '_')}` as any) ? t(`states.${state.replace(/ /g, '_')}` as any) : state, 
                                    value: state 
                                }))
                            ]}
                        />
                    </div>
                    <div>
                        <label className="block text-xs font-semibold mb-1.5 label-tag">{t('district')}</label>
                        <CustomSelect
                            value={selectedDistrict}
                            onChange={handleDistrictChange}
                            disabled={!selectedState || selectedState === "GPS Enabled"}
                            placeholder={t('select_district')}
                            options={[
                                ...(selectedState === "GPS Enabled" ? [{ label: "Auto-Detect", value: "Auto" }] : []),
                                ...districts.map(d => ({ label: getDistrictLabel(d), value: d }))
                            ]}
                        />
                    </div>

                    {/* Taluk Dropdown ONLY for Tamil Nadu */}
                    {selectedState === "Tamil Nadu" && (
                        <div>
                            <label className="block text-xs font-semibold mb-1.5 label-tag">{t('taluk')}</label>
                            <CustomSelect
                                value={selectedTaluk}
                                onChange={handleTalukChange}
                                disabled={!selectedDistrict}
                                placeholder={t('select_taluk')}
                                options={
                                    (selectedDistrict && TN_TALUKS[selectedDistrict])
                                        ? Object.keys(TN_TALUKS[selectedDistrict]).sort().map(ta => ({ label: getTalukLabel(ta), value: ta }))
                                        : []
                                }
                            />
                        </div>
                    )}
                </div>

                {/* Location Status */}
                {locStatus && (
                    <div className="text-sm font-medium px-3 py-1.5 rounded-lg inline-block" style={{ color: 'var(--green-brand)', background: 'var(--cream-dark)', border: '1px solid var(--green-accent)' }}>
                        {locStatus}
                    </div>
                )}

                {/* Commodity + Variety + Quantity + Search */}
                <div className="flex gap-3 flex-wrap items-end">
                    <div className="w-[calc(50%-6px)] md:w-36">
                        <label className="block text-xs font-semibold mb-1.5 label-tag">{t('commodity')}</label>
                        <CustomSelect
                            value={selectedCommodity}
                            onChange={setSelectedCommodity}
                            placeholder="Select Commodity"
                            options={COMMODITIES.map(c => ({ label: getCommodityLabel(c), value: c }))}
                        />
                    </div>
                    <div className="w-[calc(50%-6px)] md:w-36">
                        <label className="block text-xs font-semibold mb-1.5 label-tag">{t('variety')}</label>
                        <CustomSelect
                            value={selectedVariety}
                            onChange={setSelectedVariety}
                            placeholder={t('all_varieties')}
                            options={(COMMODITY_VARIETIES[selectedCommodity] || []).map(v => ({ label: getVarietyLabel(v), value: v }))}
                        />
                    </div>
                    <div className="w-[calc(50%-6px)] md:w-32 flex-grow">
                        <label className="block text-xs font-semibold mb-1.5 label-tag">{t('quantity')}</label>
                        <div className="flex items-center gap-2">
                            <button
                                onClick={() => setQuantity(Math.max(1, quantity - 1))}
                                className="flex items-center justify-center font-bold rounded-lg h-11 w-11 transition-all"
                                style={{ background: 'var(--cream-dark)', border: '1.5px solid var(--card-border)', color: 'var(--text-dark)' }}
                            >-</button>
                            <input
                                type="number"
                                min="1"
                                value={quantity}
                                onChange={(e) => { const v = Number(e.target.value); setQuantity(v > 0 ? v : 1); }}
                                className="w-full rounded-lg h-11 px-3 text-center text-sm focus:outline-none"
                                style={{ background: '#fff', border: '1.5px solid var(--card-border)', color: 'var(--text-dark)' }}
                            />
                            <button
                                onClick={() => setQuantity(quantity + 1)}
                                className="flex items-center justify-center font-bold rounded-lg h-11 w-11 transition-all"
                                style={{ background: 'var(--cream-dark)', border: '1.5px solid var(--card-border)', color: 'var(--text-dark)' }}
                            >+</button>
                        </div>
                    </div>
                    <div className="w-[calc(50%-6px)] md:w-36">
                        <label className="block text-xs font-semibold mb-1.5 label-tag">{t('date')}</label>
                        <CustomDatePicker
                            value={selectedDate}
                            max={new Date().toISOString().split('T')[0]}
                            onChange={setSelectedDate}
                            placeholder={t('date')}
                        />
                    </div>
                    <button
                        onClick={handleSearch}
                        disabled={loading || !selectedState || !selectedDistrict}
                        className="btn-green flex items-center justify-center gap-2 h-11 px-6 text-sm w-full md:w-auto mt-2 md:mt-0"
                    >
                        {loading ? t('calculating') : <><Search size={16} /> {t('find_price')}</>}
                    </button>
                </div>
            </div>

            {/* MAP COMPONENT */}
            {location && results.length > 0 && (
                <div className="w-full">
                    <h3 className="text-lg font-semibold mb-2">{t('map_title')}</h3>
                    <MandiMap
                        userLat={location.lat}
                        userLon={location.lon}
                        mandis={results.map(r => ({
                            mandi: getMandiLabel(r.mandi),
                            lat: r.lat,
                            lon: r.lon,
                            price: r.price_per_qtl,
                            profit: r.net_profit
                        }))}
                    />
                </div>
            )}

            <div className="space-y-3 max-h-[420px] overflow-y-auto custom-scrollbar pr-1 mt-2">
                {results.length === 0 && !loading && !hasSearched && (
                    <p className="text-center text-sm py-6" style={{ color: 'var(--text-muted)' }}>{t('select_hint')}</p>
                )}

                {results.length === 0 && !loading && hasSearched && (
                    <div className="rounded-xl p-5 text-center" style={{ background: '#fffbeb', border: '1.5px solid #fde68a' }}>
                        <p className="font-bold mb-1" style={{ color: '#b45309' }}>{t('no_live_data')}</p>
                        <p className="text-xs leading-relaxed" style={{ color: '#92400e' }}>
                            {t('agmarknet_fail', { commodity: selectedCommodity })}
                        </p>
                    </div>
                )}

                {results.map((mandi, idx) => (
                    <div
                        key={idx}
                        className="rounded-xl overflow-hidden transition-all duration-300 hover:shadow-lg hover:-translate-y-1 group"
                        style={{
                            background: expandedMandi === mandi.mandi ? 'var(--cream-dark)' : '#fff',
                            border: `1.5px solid ${expandedMandi === mandi.mandi ? 'var(--green-brand)' : 'var(--card-border)'}`,
                            boxShadow: expandedMandi === mandi.mandi ? '0 0 0 4px rgba(34,164,71,0.1)' : '0 4px 14px rgba(0,0,0,0.03)',
                        }}
                    >
                        <div
                            className="p-4 flex justify-between items-center cursor-pointer"
                            onClick={() => toggleExpand(mandi)}
                        >
                            <div>
                                <h3 className="font-bold text-sm flex items-center gap-2" style={{ color: 'var(--text-dark)' }}>
                                    {mandi.translated_name || getMandiLabel(mandi.mandi)}
                                    {expandedMandi === mandi.mandi
                                        ? <span className="text-xs px-2 py-0.5 rounded-full text-white" style={{ background: 'var(--green-brand)' }}>{t('selected')}</span>
                                        : <span className="text-xs" style={{ color: 'var(--text-muted)' }}>{t('click_details')}</span>
                                    }
                                </h3>
                                <div className="flex gap-3 text-xs mt-1 items-center flex-wrap">
                                    <span className="flex items-center gap-1" style={{ color: 'var(--text-muted)' }}><Truck size={12} /> {mandi.distance_km} km</span>
                                    <span className="flex items-center gap-1" style={{ color: 'var(--text-muted)' }}>
                                        <DollarSign size={12} /> ₹{mandi.price_per_qtl.toLocaleString('en-IN', { maximumFractionDigits: 0 })}/qtl
                                    </span>
                                    {mandi.is_predicted && (
                                        <span
                                            className="text-xs px-2 py-0.5 rounded-full font-semibold"
                                            style={{ color: '#92400e', background: '#fef3c7', border: '1px solid #fde68a' }}
                                            title={`AI projection from last data on ${mandi.last_updated}`}
                                        >
                                            {t('ai_projected')}
                                        </span>
                                    )}
                                </div>
                            </div>
                            <div className="text-right">
                                <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{t('net_profit')}</p>
                                <p className={`text-lg font-bold`} style={{ color: mandi.net_profit >= 0 ? 'var(--green-brand)' : '#ef4444' }}>
                                    ₹{mandi.net_profit.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                                </p>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default MandiFinder;
