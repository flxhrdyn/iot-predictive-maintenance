import { useState, useEffect } from 'react';
import { Thermometer, RotateCcw, Gauge, Wrench } from 'lucide-react';

// Components
import { Sidebar } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { InfoItem } from './components/common/InfoItem';
import { MetricCard } from './components/telemetry/MetricCard';
import { RiskBadge } from './components/telemetry/RiskBadge';
import { FailureChart } from './components/analytics/FailureChart';
import { EventLog } from './components/analytics/EventLog';

// Hooks
import { useTelemetry } from './hooks/useTelemetry';

function App() {
  const { data: telemetry, status } = useTelemetry('http://localhost:8000/telemetry/latest', 1000);
  const [chartData, setChartData] = useState<number[]>(Array(30).fill(0));
  const [logs, setLogs] = useState<string[]>([]);

  useEffect(() => {
    if (telemetry) {
      setChartData(prev => {
        const newData = [...prev, telemetry.prediction.failure_probability * 100];
        return newData.slice(-30);
      });

      if (telemetry.prediction.risk_level === 'HIGH') {
        const msg = `[WARNING] High risk detected on ${telemetry.prediction.device_id}!`;
        setLogs(prev => [`[${new Date().toLocaleTimeString()}] ${msg}`, ...prev].slice(0, 10));
      }
    }
  }, [telemetry]);

  if (status === 'OFFLINE') {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-rose-50 p-6">
        <div className="max-w-md w-full bg-white border-2 border-rose-100 rounded-3xl p-8 shadow-xl text-center">
          <div className="w-16 h-16 bg-rose-100 text-rose-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <Wrench size={32} />
          </div>
          <h2 className="text-xl font-black text-slate-800 uppercase mb-2">System Offline</h2>
          <p className="text-slate-500 text-sm mb-6 font-medium">Unable to connect to the Predictive Maintenance API. Please ensure the backend services are running.</p>
          <button 
            onClick={() => window.location.reload()}
            className="w-full bg-slate-900 text-white font-black py-3 rounded-xl hover:bg-slate-800 transition-colors uppercase text-xs tracking-widest"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  if (!telemetry) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-slate-50">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="font-black text-slate-400 uppercase tracking-widest text-xs">Initializing System...</p>
          <p className="text-[10px] font-bold text-slate-300 uppercase tracking-tight">Waiting for first telemetry packet...</p>
        </div>
      </div>
    );
  }

  const { reading: sensor, prediction: pred } = telemetry;

  return (
    <div className="flex min-h-screen w-full">
      <Sidebar status={status} />

      <main className="flex-1 flex flex-col h-screen overflow-hidden bg-slate-50">
        <Header />

        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-4">
              <RiskBadge level={pred.risk_level} probability={pred.failure_probability} />
            </div>

            <div className="bg-white border border-slate-200 rounded-xl p-6 lg:col-span-8 shadow-sm">
              <h2 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-6">Asset Identification</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <InfoItem label="Device Node" value={pred.device_id || 'PLC-AG-001'} highlight />
                <InfoItem label="Asset Type" value="CNC Milling" />
                <InfoItem label="Machine Class" value={sensor.type} />
                <InfoItem label="AI Latency" value={`${pred.inference_time_ms} ms`} warning />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricCard label="Process Temperature" subLabel="°KELVIN x10" value={sensor.process_temperature_K.toFixed(1)} unit="K" icon={<Thermometer />} color="rose" progress={((sensor.process_temperature_K - 290) / 30) * 100} />
            <MetricCard label="Engine RPM" subLabel="ROTATIONAL SPEED" value={sensor.rotational_speed_rpm.toFixed(0)} unit="rpm" icon={<RotateCcw />} color="blue" progress={(sensor.rotational_speed_rpm / 3000) * 100} />
            <MetricCard label="Applied Torque" subLabel="APPLIED TORSION" value={sensor.torque_Nm.toFixed(1)} unit="Nm" icon={<Gauge />} color="amber" progress={(sensor.torque_Nm / 80) * 100} />
            <MetricCard label="Tool Wear" subLabel="CUMULATIVE STRESS" value={sensor.tool_wear_min.toFixed(0)} unit="min" icon={<Wrench />} color="emerald" progress={(sensor.tool_wear_min / 250) * 100} />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 pb-10">
            <div className="lg:col-span-2">
              <FailureChart data={chartData} />
            </div>
            <EventLog logs={logs} />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
