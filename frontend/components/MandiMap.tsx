'use client';

import { useEffect, useRef } from 'react';

interface MandiMapProps {
    userLat: number;
    userLon: number;
    mandis: Array<{
        mandi: string;
        lat: number;
        lon: number;
        price: number;
        profit: number;
    }>;
}

// SVG pin helper — color is the fill, label is a tiny text inside
function makePinIcon(L: typeof import('leaflet'), color: string) {
    return L.divIcon({
        className: '',
        html: `
            <svg xmlns="http://www.w3.org/2000/svg" width="28" height="40" viewBox="0 0 28 40">
                <path d="M14 0C6.268 0 0 6.268 0 14c0 9.333 14 26 14 26S28 23.333 28 14C28 6.268 21.732 0 14 0z"
                      fill="${color}" stroke="#fff" stroke-width="2"/>
                <circle cx="14" cy="14" r="6" fill="#fff" opacity="0.85"/>
            </svg>`,
        iconSize: [28, 40],
        iconAnchor: [14, 40],
        popupAnchor: [0, -42],
    });
}

export default function MandiMap({ userLat, userLon, mandis = [] }: MandiMapProps) {
    const mapRef = useRef<HTMLDivElement>(null);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const leafletMapRef = useRef<any>(null);

    useEffect(() => {
        let isMounted = true;

        import('leaflet').then((L) => {
            if (!isMounted) return;
            import('leaflet/dist/leaflet.css' as never);

            // Prevent double-init (React Strict Mode)
            if (!mapRef.current || leafletMapRef.current) return;

            const greenIcon = makePinIcon(L, '#22c55e');  // farmer — green-500
            const blueIcon = makePinIcon(L, '#3b82f6');  // mandis — blue-500

            // If the map container was somehow initialized previously to Leaflet, clean it
            const container = mapRef.current;
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            if ((container as any)._leaflet_id) {
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                (container as any)._leaflet_id = null;
            }

            const map = L.map(container, { scrollWheelZoom: false }).setView([userLat, userLon], 9);
            leafletMapRef.current = map;

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            }).addTo(map);

            // 🟢 Farmer location — green pin
            L.marker([userLat, userLon], { icon: greenIcon })
                .addTo(map)
                .bindPopup('<div style="font-weight:bold;color:#166534;">📍 Your Location (Farmer)</div>');

            // 🔵 Mandi locations — blue pins
            mandis.forEach((m) => {
                L.marker([m.lat, m.lon], { icon: blueIcon })
                    .addTo(map)
                    .bindPopup(
                        `<div style="color:#1e3a5f;">
                            <div style="font-weight:bold;">${m.mandi}</div>
                            <div>Price: ₹${m.price.toLocaleString('en-IN', { maximumFractionDigits: 2 })}/qtl</div>
                            <div style="color:#16a34a;font-weight:600;">Profit: ₹${m.profit.toLocaleString('en-IN', { maximumFractionDigits: 2 })}</div>
                        </div>`
                    );
            });
        });

        return () => {
            isMounted = false;
            if (leafletMapRef.current) {
                leafletMapRef.current.remove();
                leafletMapRef.current = null;
            }
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    // Update view when farmer coordinates change
    useEffect(() => {
        if (leafletMapRef.current) {
            leafletMapRef.current.setView([userLat, userLon], 9);
        }
    }, [userLat, userLon]);

    return (
        <div
            ref={mapRef}
            className="h-[400px] w-full rounded-xl overflow-hidden shadow-[0_8px_30px_rgb(0,0,0,0.08)] border border-gray-200 z-0"
        />
    );
}
