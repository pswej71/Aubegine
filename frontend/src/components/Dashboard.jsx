import React, { useState, useEffect } from 'react';
import {
    LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { Activity, Zap, Cpu, AlertTriangle, Lightbulb, TrendingUp, Sun, Wind, Thermometer } from 'lucide-react';
import { getLatestTelemetry, getAlerts, getGenAIAnalysis, postTelemetry } from '../api';
import { format } from 'date-fns';

const StatCard = ({ title, value, unit, icon: Icon, color, delay }) => (
    <div className={`glass-card metric-card fade-in ${delay}`}>
        <div className="metric-header">
            {title}
            <Icon size={20} color={color} />
        </div>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem' }}>
            <div className="metric-value">{value}</div>
            <span style={{ color: 'var(--text-secondary)', fontWeight: 600 }}>{unit}</span>
        </div>
    </div>
);

const Dashboard = () => {
    const [latestData, setLatestData] = useState({});
    const [historicalData, setHistoricalData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [modelMode, setModelMode] = useState('auto');

    const refreshSystemState = async () => {
        try {
            const [prediction, alerts, rca] = await Promise.all([
                getLatestTelemetry('DEMO-001'),
                getAlerts('DEMO-001'),
                getGenAIAnalysis('DEMO-001')
            ]);

            setLatestData({
                prediction,
                alerts,
                rca,
                timeLabel: format(new Date(), 'HH:mm:ss')
            });

            // Maintain a small historical buffer for charts
            setHistoricalData(prev => {
                const updated = [...prev, { ...prediction, timeLabel: format(new Date(), 'HH:mm:ss') }];
                return updated.slice(-30);
            });

            setLoading(false);
        } catch (error) {
            console.error("API Sync Error:", error);
            setLoading(false);
        }
    };

    useEffect(() => {
        const socket = new WebSocket('ws://localhost:8000/ws');

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.mac === 'DEMO-001') {
                setLatestData({
                    prediction: data.prediction,
                    anomaly: data.anomaly,
                    rca: data.rca,
                    telemetry: data.telemetry,
                    timeLabel: format(new Date(), 'HH:mm:ss')
                });

                setHistoricalData(prev => {
                    const updated = [...prev, {
                        ...data.prediction,
                        ...data.telemetry,
                        timeLabel: format(new Date(), 'HH:mm:ss')
                    }];
                    return updated.slice(-30);
                });
            }
        };

        return () => socket.close();
    }, []);

    // Initial load and simulation
    useEffect(() => {
        refreshSystemState();
        const simulator = setInterval(() => {
            const mockTelemetry = {
                mac: 'DEMO-001',
                dc_voltage: 480 + Math.random() * 20,
                dc_current: 10 + Math.random() * 2,
                ac_voltage: 230 + Math.random() * 5,
                ac_current: 15 + Math.random() * 3,
                grid_voltage: 230 + Math.random() * 2,
                power_output_ac: 4500 + Math.random() * 1000,
                inverter_temperature: 40 + Math.random() * 15,
                ambient_temperature: 25 + Math.random() * 5,
                solar_irradiance: 800 + Math.random() * 200
            };

            postTelemetry(mockTelemetry, modelMode);
        }, 10000); // Push every 10s for demo
        return () => clearInterval(simulator);
    }, [modelMode]);

    const latest = latestData.prediction || {};
    const rca = latestData.rca || {};

    // Parse RCA if it's a string
    let parsedRCA = rca;
    if (typeof rca === 'string' && rca.startsWith('{')) {
        try { parsedRCA = JSON.parse(rca); } catch (e) { }
    }

    return (
        <div className="main-content">
            {/* Model Selection UI */}
            <div className="glass-card fade-in stagger-1" style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <Cpu size={24} color="var(--accent-primary)" />
                    <div>
                        <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>System Intelligence Mode</h3>
                        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                            Active: <span className="gradient-text" style={{ fontWeight: 700 }}>{latest.model_type?.toUpperCase() || modelMode.toUpperCase()}</span>
                        </p>
                    </div>
                </div>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                    {['internal', 'combined', 'auto'].map(m => (
                        <button
                            key={m}
                            className={`btn ${modelMode === m ? '' : 'btn-outline'}`}
                            onClick={() => setModelMode(m)}
                            style={{
                                opacity: modelMode === m ? 1 : 0.6,
                                background: modelMode === m ? 'var(--accent-primary)' : 'rgba(255,255,255,0.05)',
                                border: modelMode === m ? 'none' : '1px solid var(--border-color)'
                            }}
                        >
                            {m.charAt(0).toUpperCase() + m.slice(1)}
                        </button>
                    ))}
                </div>
            </div>

            <div className="dashboard-grid">
                <StatCard
                    title="Failure Probability"
                    value={latest.failure_probability ? (latest.failure_probability * 100).toFixed(1) : '0.0'}
                    unit="%"
                    icon={AlertTriangle}
                    color={latest.risk_level === 'High' ? 'var(--accent-danger)' : 'var(--accent-warning)'}
                    delay="stagger-1"
                />
                <StatCard
                    title="Risk Assessment"
                    value={latest.risk_level || 'Normal'}
                    unit=""
                    icon={Activity}
                    color={latest.risk_level === 'High' ? 'var(--accent-danger)' : 'var(--accent-success)'}
                    delay="stagger-2"
                />
                <StatCard
                    title="Predicted Power"
                    value={latest.predicted_power ? latest.predicted_power.toFixed(1) : '0.0'}
                    unit="W"
                    icon={Zap}
                    color="var(--accent-primary)"
                    delay="stagger-3"
                />
                <StatCard
                    title="Predicted Efficiency"
                    value={latest.predicted_efficiency ? latest.predicted_efficiency.toFixed(1) : '0.0'}
                    unit="%"
                    icon={Cpu}
                    color="var(--accent-success)"
                    delay="stagger-4"
                />
            </div>

            <div className="main-charts-grid">
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                    <div className="glass-card fade-in stagger-2" style={{ height: '400px' }}>
                        <h3 className="chart-container-title">Power Generation Tracking (W)</h3>
                        <ResponsiveContainer width="100%" height="85%">
                            <AreaChart data={historicalData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                                <defs>
                                    <linearGradient id="colorPower" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="var(--accent-primary)" stopOpacity={0.8} />
                                        <stop offset="95%" stopColor="var(--accent-primary)" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                                <XAxis dataKey="timeLabel" stroke="var(--text-secondary)" tick={{ fontSize: 12 }} />
                                <YAxis stroke="var(--text-secondary)" tick={{ fontSize: 12 }} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', border: '1px solid var(--border-color)', borderRadius: '8px' }}
                                />
                                <Area type="monotone" dataKey="predicted_power" stroke="var(--accent-primary)" fillOpacity={1} fill="url(#colorPower)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>

                    <div className="glass-card fade-in stagger-3" style={{ height: '350px' }}>
                        <h3 className="chart-container-title">Inverter Efficiency & Thermal Stress</h3>
                        <ResponsiveContainer width="100%" height="85%">
                            <LineChart data={historicalData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                                <XAxis dataKey="timeLabel" stroke="var(--text-secondary)" />
                                <YAxis stroke="var(--text-secondary)" />
                                <Tooltip contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', border: '1px solid var(--border-color)' }} />
                                <Legend />
                                <Line type="monotone" dataKey="predicted_efficiency" stroke="var(--accent-success)" strokeWidth={3} name="Efficiency %" />
                                <Line type="monotone" dataKey="failure_probability" stroke="var(--accent-danger)" strokeWidth={2} name="Failure Risk" />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                    <div className="glass-card fade-in stagger-3">
                        <h3 className="chart-container-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <Lightbulb color="var(--accent-warning)" />
                            GenAI Diagnostic Insights
                        </h3>
                        {loading ? (
                            <p style={{ color: 'var(--text-secondary)' }}>Processing telemetry...</p>
                        ) : parsedRCA.detected_issue ? (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                    <span className={`badge ${latest.risk_level === 'Low' ? 'badge-success' : 'badge-danger'}`}>
                                        Status: {latest.risk_level}
                                    </span>
                                </div>
                                <div style={{ background: 'rgba(59, 130, 246, 0.1)', padding: '1rem', borderRadius: '8px', borderLeft: '4px solid var(--accent-primary)' }}>
                                    <h4 style={{ color: 'var(--accent-primary)', fontSize: '0.875rem', marginBottom: '0.5rem', fontWeight: 700 }}>{parsedRCA.detected_issue}</h4>

                                    {parsedRCA.possible_causes && (
                                        <div style={{ marginBottom: '0.5rem' }}>
                                            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Possible Causes</p>
                                            <ul style={{ fontSize: '0.875rem', paddingLeft: '1.2rem' }}>
                                                {Array.isArray(parsedRCA.possible_causes) ? parsedRCA.possible_causes.map((c, i) => <li key={i}>{c}</li>) : <li>{parsedRCA.possible_causes}</li>}
                                            </ul>
                                        </div>
                                    )}

                                    <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Recommended Actions</p>
                                    <p style={{ fontSize: '0.875rem' }}>{parsedRCA.recommended_maintenance_actions || parsedRCA.recommended_actions}</p>
                                </div>
                            </div>
                        ) : <p style={{ color: 'var(--text-secondary)' }}>{typeof rca === 'string' ? rca : "Optimal operation detected."}</p>}
                    </div>

                    <div className="glass-card fade-in stagger-4">
                        <h3 className="chart-container-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <AlertTriangle color="var(--accent-danger)" />
                            Real-Time Alerts
                        </h3>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                            {latestData.anomaly?.is_anomaly && (
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.75rem', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px', border: '1px solid var(--accent-danger)' }}>
                                    <AlertTriangle size={18} color="var(--accent-danger)" />
                                    <div>
                                        <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>Technical Anomaly Detected</div>
                                        <div style={{ fontSize: '0.75rem', opacity: 0.8 }}>Score: {latestData.anomaly.anomaly_score}</div>
                                    </div>
                                </div>
                            )}
                            {latest.safety_alerts?.map((msg, i) => (
                                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.75rem', background: 'rgba(245, 158, 11, 0.1)', borderRadius: '8px' }}>
                                    <Zap size={18} color="var(--accent-warning)" />
                                    <div style={{ fontSize: '0.875rem' }}>{msg}</div>
                                </div>
                            ))}
                            {!latestData.anomaly?.is_anomaly && (!latest.safety_alerts || latest.safety_alerts.length === 0) && (
                                <p style={{ color: 'var(--text-secondary)', textAlign: 'center' }}>No active alerts.</p>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
