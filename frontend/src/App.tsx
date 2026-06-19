import React, { useState, useEffect } from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, AlertTriangle, Map, Calculator, MessageSquare, Settings as SettingsIcon } from 'lucide-react';
import axios from 'axios';
import Plot from 'react-plotly.js';

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// --- COMPONENTS ---

const Sidebar = () => {
  const location = useLocation();
  const links = [
    { name: 'Dashboard', path: '/dashboard', icon: <LayoutDashboard size={20} /> },
    { name: 'Violations', path: '/violations', icon: <AlertTriangle size={20} /> },
    { name: 'Corridors', path: '/corridors', icon: <Map size={20} /> },
    { name: 'Calculator', path: '/calculator', icon: <Calculator size={20} /> },
    { name: 'SMS Preview', path: '/sms-preview', icon: <MessageSquare size={20} /> },
    { name: 'Settings', path: '/settings', icon: <SettingsIcon size={20} /> },
  ];

  return (
    <div className="w-64 bg-card h-screen fixed left-0 top-0 border-r border-white/10 p-4 flex flex-col">
      <div className="flex items-center gap-3 mb-8 px-2">
        <span className="text-2xl">🚗</span>
        <h1 className="text-xl font-bold text-white tracking-wide">ParkImpact AI</h1>
      </div>
      <nav className="flex-1 space-y-2">
        {links.map((link) => (
          <Link
            key={link.name}
            to={link.path}
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
              location.pathname === link.path || (location.pathname === '/' && link.path === '/dashboard')
                ? 'bg-primary/20 text-primary border border-primary/30'
                : 'text-gray-400 hover:bg-white/5 hover:text-white'
            }`}
          >
            {link.icon}
            <span className="font-medium">{link.name}</span>
          </Link>
        ))}
      </nav>
      <div className="mt-auto p-4 bg-primary/10 rounded-lg border border-primary/20">
        <p className="text-xs text-primary font-bold mb-1">IMPACT-BASED SYSTEM</p>
        <p className="text-xs text-gray-400">First in India dynamic fine allocation prototype.</p>
      </div>
    </div>
  );
};

// --- PAGES ---

const Dashboard = () => {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-white mb-2">Impact Analytics Dashboard</h1>
      <p className="text-gray-400 mb-8">Real-time analysis of parking congestion damage and fine generation.</p>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="glass-panel p-6">
          <p className="text-sm text-gray-400 font-bold tracking-wider mb-1">TOTAL VIOLATIONS</p>
          <p className="text-3xl font-bold text-white">115,400</p>
        </div>
        <div className="glass-panel p-6">
          <p className="text-sm text-primary font-bold tracking-wider mb-1">DISCOVERED HOTSPOTS</p>
          <p className="text-3xl font-bold text-white">206</p>
          <p className="text-xs text-primary mt-2">via DBSCAN clustering</p>
        </div>
        <div className="glass-panel p-6">
          <p className="text-sm text-warning font-bold tracking-wider mb-1">NO JUNCTION RECORDS</p>
          <p className="text-3xl font-bold text-white">47%</p>
          <p className="text-xs text-warning mt-2">Previously invisible</p>
        </div>
        <div className="glass-panel p-6 border border-danger/30">
          <p className="text-sm text-danger font-bold tracking-wider mb-1">TOP PILOT STATION</p>
          <p className="text-2xl font-bold text-white">Upparpet</p>
          <p className="text-xs text-danger mt-2">135,336 Impact Score</p>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-panel p-6">
          <h3 className="text-lg font-bold mb-4">Why This Is Unique (ROI)</h3>
          <p className="text-gray-300 mb-4">Transitioning from a fixed ₹500 fine to an impact-based dynamic fine (₹530-₹5,000+) ensures penalties match actual traffic damage caused.</p>
          <div className="flex items-center gap-4">
            <div className="bg-white/5 p-4 rounded flex-1 text-center border border-white/10">
              <p className="text-xs text-gray-400 mb-1">CURRENT</p>
              <p className="text-xl font-bold text-white">₹500 <span className="text-sm font-normal">fixed</span></p>
            </div>
            <div className="text-primary font-bold">➔</div>
            <div className="bg-primary/20 p-4 rounded flex-1 text-center border border-primary/30">
              <p className="text-xs text-primary mb-1">DYNAMIC IMPACT</p>
              <p className="text-xl font-bold text-white">~₹2,000 <span className="text-sm font-normal">avg</span></p>
            </div>
          </div>
          <p className="text-center text-success font-bold mt-4">+300% Revenue Increase for High-Impact Zones</p>
        </div>
        
        <div className="glass-panel p-6">
           <h3 className="text-lg font-bold mb-4">Vehicle Impact Distribution</h3>
           <Plot
            data={[{
              values: [50, 30, 10, 10],
              labels: ['Cars (2.5x)', 'Scooters (0.8x)', 'Trucks (4.5x)', 'Others'],
              type: 'pie',
              hole: .6,
              marker: { colors: ['#4ea8de', '#2a9d8f', '#e63946', '#f4a261'] }
            }]}
            layout={{ 
              paper_bgcolor: 'rgba(0,0,0,0)', 
              plot_bgcolor: 'rgba(0,0,0,0)', 
              font: { color: '#fff' },
              height: 200,
              margin: { t: 0, b: 0, l: 0, r: 0 }
            }}
            config={{ displayModeBar: false }}
          />
        </div>
      </div>
    </div>
  );
};

const CalculatorPage = () => {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    congestion_level: 8,
    vehicles_per_min: 3,
    duration_min: 30,
    vehicle_type: "Car",
    location: "Upparpet",
    hour: 9
  });

  const handleCalculate = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${API_URL}/api/calculator/calculate`, formData);
      setResult(res.data);
    } catch (e) {
      console.error(e);
      alert("Error calculating fine");
    }
    setLoading(false);
  };

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-white mb-2">Impact Fine Calculator</h1>
      <p className="text-gray-400 mb-8">Manually calculate dynamic fines based on economic damage equations.</p>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="glass-panel p-6">
          <h3 className="text-xl font-bold mb-6 border-b border-white/10 pb-4">Parameters</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-1">Vehicle Type</label>
              <select className="w-full bg-gray-800 border border-gray-700 rounded p-2 text-white" value={formData.vehicle_type} onChange={e=>setFormData({...formData, vehicle_type: e.target.value})}>
                <option value="Car">Car (2.5x)</option>
                <option value="Scooter">Scooter (0.8x)</option>
                <option value="Truck">Truck (4.5x)</option>
                <option value="Maxi-cab">Maxi-cab (3.0x)</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-1">Location Zone</label>
              <select className="w-full bg-gray-800 border border-gray-700 rounded p-2 text-white" value={formData.location} onChange={e=>setFormData({...formData, location: e.target.value})}>
                <option value="Upparpet">Upparpet (5.0x)</option>
                <option value="Shivajinagar">Shivajinagar (4.5x)</option>
                <option value="HAL Old Airport">HAL Old Airport (4.0x)</option>
                <option value="Other">Other (2.0x)</option>
              </select>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">Hour of Day (IST)</label>
                <input type="number" className="w-full bg-gray-800 border border-gray-700 rounded p-2 text-white" value={formData.hour} onChange={e=>setFormData({...formData, hour: parseInt(e.target.value)})} min={0} max={23} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">Duration (mins)</label>
                <input type="number" className="w-full bg-gray-800 border border-gray-700 rounded p-2 text-white" value={formData.duration_min} onChange={e=>setFormData({...formData, duration_min: parseInt(e.target.value)})} />
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">Congestion Level (1-10)</label>
                <input type="number" className="w-full bg-gray-800 border border-gray-700 rounded p-2 text-white" value={formData.congestion_level} onChange={e=>setFormData({...formData, congestion_level: parseInt(e.target.value)})} min={1} max={10} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">Vehicles/Min Flow</label>
                <input type="number" className="w-full bg-gray-800 border border-gray-700 rounded p-2 text-white" value={formData.vehicles_per_min} onChange={e=>setFormData({...formData, vehicles_per_min: parseInt(e.target.value)})} />
              </div>
            </div>
            
            <button onClick={handleCalculate} disabled={loading} className="w-full bg-primary hover:bg-primary/80 text-white font-bold py-3 rounded mt-4 transition-colors">
              {loading ? 'Calculating...' : 'Calculate Congestion Impact Charge'}
            </button>
          </div>
        </div>
        
        {result && (
          <div className="glass-panel p-6 flex flex-col justify-center items-center bg-gradient-to-br from-[#1a1a2e] to-[#16213e]">
            <h3 className="text-warning font-bold tracking-widest text-sm mb-2">ECONOMIC DAMAGE</h3>
            <p className="text-4xl font-bold text-white mb-8">₹{result.economic_damage.toLocaleString()}</p>
            
            <h3 className="text-primary font-bold tracking-widest text-sm mb-2">RECOMMENDED TOTAL FINE</h3>
            <p className="text-6xl font-black text-white mb-2 shadow-sm">₹{result.total_fine.toLocaleString()}</p>
            <p className="text-gray-400 text-sm mb-8">Base (₹{result.base_fine}) + Impact Charge (₹{result.congestion_charge.toLocaleString()})</p>
            
            <div className="w-full bg-white/5 rounded p-4 border border-white/10 text-center">
              <p className="text-sm text-gray-300">This violation delayed <span className="font-bold text-white">{result.vehicles_delayed} vehicles</span>.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const SMSPreview = () => {
  const [sms, setSms] = useState<string>("");
  
  useEffect(() => {
    const fetchSms = async () => {
      try {
        const res = await axios.post(`${API_URL}/api/sms/generate`, {
          vehicle_number: "KA-01-AB-1234",
          junction_name: "KR Market Junction",
          police_station: "City Market",
          hour: 9,
          duration_min: 30,
          charge: 11550,
          weight: 2.5,
          vehicle_type: "Car",
          location: 4.0,
          hour_mult: 5.5,
          peak_status: "Morning Peak",
          total: 12050,
          vehicles_delayed: 720,
          hours_wasted: 36,
          economic_damage: 21600
        });
        setSms(res.data.sms);
      } catch (e) {
        console.error(e);
      }
    };
    fetchSms();
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-white mb-2">SMS Template Preview</h1>
      <p className="text-gray-400 mb-8">Automated notification format showing impact transparency to offenders.</p>
      
      <div className="max-w-md mx-auto glass-panel p-0 overflow-hidden border-t-8 border-t-primary">
        <div className="bg-[#1e1e1e] p-6 text-sm font-mono whitespace-pre-wrap leading-relaxed text-gray-300">
          {sms || "Loading template..."}
        </div>
      </div>
    </div>
  );
};

const Corridors = () => {
  const [corridors, setCorridors] = useState<any[]>([]);

  useEffect(() => {
    axios.get(`${API_URL}/api/corridors/top15`).then(res => setCorridors(res.data)).catch(console.error);
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-white mb-2">Top 15 Enforcement Corridors</h1>
      <p className="text-gray-400 mb-8">Ranked by greedy allocation impact score. Two of the top six are discovered micro-hotspots.</p>
      
      <div className="glass-panel overflow-hidden">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-white/5 border-b border-white/10">
              <th className="p-4 text-gray-400 font-medium">Rank</th>
              <th className="p-4 text-gray-400 font-medium">Corridor / Junction</th>
              <th className="p-4 text-gray-400 font-medium">Station</th>
              <th className="p-4 text-gray-400 font-medium">Peak (IST)</th>
              <th className="p-4 text-gray-400 font-medium text-right">Impact Score</th>
            </tr>
          </thead>
          <tbody>
            {corridors.map((c, i) => (
              <tr key={i} className="border-b border-white/5 hover:bg-white/5">
                <td className="p-4 font-bold text-white">#{c.rank}</td>
                <td className="p-4">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-primary">{c.name}</span>
                    {c.discovered && <span className="text-[10px] bg-warning/20 text-warning px-2 py-1 rounded font-bold uppercase">Discovered</span>}
                  </div>
                </td>
                <td className="p-4 text-gray-300">{c.station}</td>
                <td className="p-4 text-gray-300">{c.peak}</td>
                <td className="p-4 text-right font-bold text-danger">{c.impact.toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const PlaceholderPage = ({ title }: { title: string }) => (
  <div className="p-8">
    <h1 className="text-3xl font-bold text-white mb-2">{title}</h1>
    <p className="text-gray-400 mb-8">This page is currently under development.</p>
  </div>
);

const App = () => {
  return (
    <div className="min-h-screen bg-dark flex">
      <Sidebar />
      <div className="flex-1 ml-64 overflow-y-auto">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/violations" element={<PlaceholderPage title="Violations List" />} />
          <Route path="/corridors" element={<Corridors />} />
          <Route path="/calculator" element={<CalculatorPage />} />
          <Route path="/sms-preview" element={<SMSPreview />} />
          <Route path="/settings" element={<PlaceholderPage title="System Settings" />} />
        </Routes>
      </div>
    </div>
  );
};

export default App;
