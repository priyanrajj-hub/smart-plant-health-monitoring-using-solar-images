import React, { useState, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Box, Plane } from '@react-three/drei';
import { Activity, Leaf, Cpu, HelpCircle, Map as MapIcon, RefreshCw, Layers } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer } from 'recharts';

function HardwareNode3D() {
    return (
        <Canvas camera={{ position: [2, 2, 2], fov: 50 }}>
            <ambientLight intensity={0.5} />
            <directionalLight position={[5, 5, 5]} intensity={1} />
            <Box args={[1, 0.5, 1]} position={[0, 0, 0]}>
                <meshStandardMaterial color="#4b5563" />
            </Box>
            <Box args={[0.2, 0.2, 0.2]} position={[0, 0.35, -0.3]}>
                <meshStandardMaterial color="#3b82f6" />
            </Box>
            <Box args={[0.1, 0.1, 0.8]} position={[0, -0.2, 0.8]}>
                <meshStandardMaterial color="#10b981" />
            </Box>
            <OrbitControls autoRotate />
        </Canvas>
    );
}

function Terrain3D({ fields }) {
    return (
        <Canvas camera={{ position: [0, 5, 10], fov: 60 }}>
            <ambientLight intensity={0.4} />
            <directionalLight position={[10, 10, 5]} intensity={1} />
            <Plane args={[20, 20]} rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.5, 0]}>
                <meshStandardMaterial color="#1f2937" />
            </Plane>
            {fields.map((f, i) => (
                <Box key={f.id} args={[1, f.fused_risk * 2, 1]} position={[(i % 2) * 3 - 1.5, f.fused_risk, Math.floor(i / 2) * 3 - 1.5]}>
                    <meshStandardMaterial color={f.fused_risk > 0.5 ? '#ef4444' : '#10b981'} />
                </Box>
            ))}
            <OrbitControls />
        </Canvas>
    );
}

export default function App() {
    const [activeTab, setActiveTab] = useState('landing');
    const [fields, setFields] = useState([]);
    const [loading, setLoading] = useState(true);
    const [dataSource, setDataSource] = useState('');

    const fetchFields = async () => {
        setLoading(true);
        try {
            const res = await fetch('http://localhost:8000/api/fields');
            const data = await res.json();
            setFields(data.fields);
            setDataSource(data.data_source);
        } catch (err) {
            // Fallback for demo
            setFields([
                { id: 1, lat: 11.0, lng: 77.0, node_id: 'NODE_01', nNDVI_score: 0.65, texture_anomaly: 0.1, temporal_change: 0.05, fused_risk: 0.15, status: 'HEALTHY_SAMPLE' },
                { id: 2, lat: 11.01, lng: 77.02, node_id: 'NODE_02', nNDVI_score: 0.40, texture_anomaly: 0.8, temporal_change: 0.9, fused_risk: 0.85, status: 'STRESS_SAMPLE' },
            ]);
            setDataSource("STATIC_SAMPLE (Backend Not Reachable)");
        }
        setLoading(false);
    };

    useEffect(() => { fetchFields(); }, []);

    const chartData = [
        { time: '10:00', risk: 0.2 }, { time: '11:00', risk: 0.25 }, { time: '12:00', risk: 0.15 }, { time: '13:00', risk: 0.8 }
    ];

    return (
        <div className="min-h-screen bg-slate-900 text-slate-100 font-sans">
            <nav className="border-b border-slate-700 bg-slate-800 px-6 py-4 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                    <Leaf className="text-emerald-500" />
                    <h1 className="text-xl font-bold tracking-tight">AGRISENSE</h1>
                </div>
                <div className="flex space-x-4">
                    <button onClick={() => setActiveTab('landing')} className={`flex items-center space-x-1 ${activeTab === 'landing' ? 'text-emerald-400' : 'text-slate-400 hover:text-white'}`}><Activity size={18} /><span>Overview</span></button>
                    <button onClick={() => setActiveTab('map')} className={`flex items-center space-x-1 ${activeTab === 'map' ? 'text-emerald-400' : 'text-slate-400 hover:text-white'}`}><MapIcon size={18} /><span>3D Map</span></button>
                    <button onClick={() => setActiveTab('hardware')} className={`flex items-center space-x-1 ${activeTab === 'hardware' ? 'text-emerald-400' : 'text-slate-400 hover:text-white'}`}><Cpu size={18} /><span>Nodes</span></button>
                    <button onClick={() => setActiveTab('about')} className={`flex items-center space-x-1 ${activeTab === 'about' ? 'text-emerald-400' : 'text-slate-400 hover:text-white'}`}><HelpCircle size={18} /><span>Algorithm</span></button>
                </div>
            </nav>

            <main className="p-6 max-w-7xl mx-auto">
                {loading && <div className="text-center p-12 text-slate-400 flex items-center justify-center"><RefreshCw className="animate-spin mr-2" /> Loading API...</div>}

                {!loading && activeTab === 'landing' && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <div className="bg-slate-800 p-8 rounded-xl border border-slate-700">
                            <h2 className="text-3xl font-light mb-4">Field Intelligence <span className="font-bold text-emerald-400">Dashboard</span></h2>
                            <p className="text-slate-400 mb-6 text-lg leading-relaxed">
                                Unifying the offline ESP32-S3 hardware ground-node with optional macro-scale RGB satellite imaging (nNDVI & Texture Anomaly) for early plant water-stress and pest detection.
                            </p>
                            <div className="p-4 bg-slate-900 rounded-lg flex items-center space-x-3">
                                <span className="relative flex h-3 w-3">
                                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                                    <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
                                </span>
                                <span className="font-mono text-sm">System Online — {dataSource}</span>
                            </div>
                        </div>

                        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
                            <h3 className="text-xl font-bold mb-4 flex items-center"><Layers className="mr-2" /> Recent Alerts (Regional Screen)</h3>
                            <div className="space-y-3">
                                {fields.map(f => (
                                    <div key={f.id} className="bg-slate-900 p-4 rounded-lg flex justify-between items-center border border-slate-700">
                                        <div>
                                            <p className="font-bold text-emerald-300">{f.node_id}</p>
                                            <p className="text-xs text-slate-500">Lat: {f.lat}, Lng: {f.lng}</p>
                                        </div>
                                        <div className="text-right">
                                            <p className="text-sm font-mono" style={{ color: f.fused_risk > 0.5 ? '#ef4444' : '#10b981' }}>Risk: {(f.fused_risk * 100).toFixed(1)}%</p>
                                            <p className="text-xs text-slate-400 uppercase">{f.status}</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {!loading && activeTab === 'map' && (
                    <div className="bg-slate-800 rounded-xl border border-slate-700 p-4 overflow-hidden h-[600px] flex flex-col">
                        <h3 className="text-xl font-bold mb-4">3D Field Map (Risk Topology)</h3>
                        <div className="flex-1 rounded-lg overflow-hidden bg-slate-950">
                            <Terrain3D fields={fields} />
                        </div>
                        <div className="mt-4 p-4 bg-slate-900 rounded-lg">
                            <h4 className="font-bold mb-2">4-Way Prediction Breakdown (Selected Field)</h4>
                            <p className="text-sm text-slate-400">1. Disease Presence: Low (Texture Layer normal)</p>
                            <p className="text-sm text-slate-400">2. Pest Presence: Low (Acoustic node baseline)</p>
                            <p className="text-sm text-slate-400">3. Nutrient: Optimal (NPK probe normal)</p>
                            <p className="text-sm text-slate-400">4. Water Stress: Normal (nNDVI stable, Capacitive sensor stable)</p>
                        </div>
                    </div>
                )}

                {!loading && activeTab === 'hardware' && (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                        <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
                            <h3 className="text-2xl font-bold mb-4">Offline ESP32-S3 Node</h3>
                            <p className="text-slate-400 mb-4 text-sm">
                                Interactive real-time offline core product. Green: FDC1004 Soil Probe. Blue: RGB Camera / Ambient module.
                            </p>
                            <div className="h-80 bg-slate-900 rounded-lg overflow-hidden border border-slate-700">
                                <HardwareNode3D />
                            </div>
                        </div>
                        <div className="bg-slate-800 rounded-xl border border-slate-700 p-6 flex flex-col">
                            <h3 className="text-xl font-bold mb-4">Sensor Time-Series & Confidence</h3>
                            <div className="flex-1 min-h-[300px]">
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={chartData}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                                        <XAxis dataKey="time" stroke="#94a3b8" />
                                        <YAxis stroke="#94a3b8" />
                                        <RechartsTooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none' }} />
                                        <Line type="monotone" dataKey="risk" stroke="#10b981" strokeWidth={3} dot={{ r: 6 }} />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    </div>
                )}

                {!loading && activeTab === 'about' && (
                    <div className="bg-slate-800 p-8 rounded-xl border border-slate-700 prose prose-invert max-w-none">
                        <h2>Algorithm Novelty & Limitations</h2>
                        <p><strong>Limitation:</strong> True NDVI requires NIR light which is absent in standard cheap drone/RGB satellite imagery. This system relies on a trained proxy index (nNDVI).</p>
                        <p><strong>Offline vs Cloud:</strong> This dashboard represents the MACRO-level optional regional cloud overlay. The true real-time, zero-latency detection relies strictly on the offline <strong>Ground Hardware Node</strong> utilizing capacitive and acoustic data directly at the plant root/leaf.</p>
                        <ul>
                            <li><strong>Temporal-change layer:</strong> Employs a rolling baseline rather than static thresholds to find flash-onset stress events.</li>
                            <li><strong>Texture-anomaly:</strong> Employs LBP (Local Binary Patterns) modeled from PlantVillage datasets to identify necrotic damage distinct from simple drought chlorosis.</li>
                        </ul>
                        <p className="text-slate-400 text-sm mt-8 border-t border-slate-700 pt-4">Data shown in this environment evaluates via synthetic fallback nodes because live NASA API credentials are unprovided.</p>
                    </div>
                )}
            </main>
        </div>
    );
}
