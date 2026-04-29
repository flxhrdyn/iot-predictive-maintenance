import { useState, useEffect } from 'react';
import { TelemetryResponse } from '../types/telemetry';

export function useTelemetry(url: string, interval: number = 1500) {
  const [data, setData] = useState<TelemetryResponse | null>(null);
  const [status, setStatus] = useState<'ONLINE' | 'OFFLINE'>('OFFLINE');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(url);
        if (!res.ok) throw new Error('API Response Error');
        const json: TelemetryResponse = await res.json();
        setData(json);
        setStatus('ONLINE');
        setError(null);
      } catch (err: any) {
        setStatus('OFFLINE');
        setError(err.message);
      }
    };

    fetchData();
    const timer = setInterval(fetchData, interval);
    return () => clearInterval(timer);
  }, [url, interval]);

  return { data, status, error };
}
