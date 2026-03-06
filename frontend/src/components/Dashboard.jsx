import React, { useState, useEffect } from 'react';
import {
    LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { Activity, Zap, Cpu, AlertTriangle, Lightbulb, TrendingUp, Sun, Wind, Thermometer } from 'lucide-react';
import { getHistory, getAISuggestions, simulateData } from '../api';
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
    const [data, setData] = useState([]);
    const [aiInsight, setAiInsight] = useState(null);
    const [loading, setLoading] = useState(true);

    const fetchData = async () => {
        try {
            const history = await getHistory(50);
            const formattedData = history.map(item => ({
                ...item,
                timeLabel: format(new Date(item.timestamp), 'HH:mm:ss')
            }));
            setData(formattedData);

            const insight = await getAISuggestions();
            setAiInsight(insight);
            setLoading(false);
        } catch (error) {
            console.error("Error fetching data:", error);
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
        // Simulate real-time by polling or websocket.
        // Given the simulator endpoint, let's poll simulator and fetch every 5s for demo.
        const interval = setInterval(() => {
            simulateData().then(() => {
                getHistory(50).then(history => {
                    const formattedData = history.map(item => ({
                        ...item,
                        timeLabel: format(new Date(item.timestamp), 'HH:mm:ss')
                    }));
                    setData(formattedData);
                });
            });
        }, 5000);

        return () => clearInterval(interval);
    }, []);

    const latest = data[data.length - 1] || {};

    return (
        <div>
            <div className="dashboard-grid">
                <StatCard
                    title="Current Power"
                    value={latest.power ? latest.power.toFixed(1) : '0.0'}
                    unit="W"
                    icon={Zap}
                    color="var(--accent-primary)"
                    delay="stagger-1"
                />
                <StatCard
                    title="Daily Energy"
                    value={latest.energy ? latest.energy.toFixed(1) : '0.0'}
                    unit="kWh"
                    icon={Activity}
                    color="var(--accent-secondary)"
                    delay="stagger-2"
                />
                <StatCard
                    title="Efficiency"
                    value={latest.efficiency ? latest.efficiency.toFixed(1) : '0.0'}
                    unit="%"
                    icon={Cpu}
                    color="var(--accent-success)"
                    delay="stagger-3"
                />
                <StatCard
                    title="Panel Temp"
                    value={latest.temperature ? latest.temperature.toFixed(1) : '0.0'}
                    unit="°C"
                    icon={Thermometer}
                    color="var(--accent-warning)"
                    delay="stagger-4"
                />
            </div>

            <div className="main-charts-grid">
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

                    <div className="glass-card fade-in stagger-2" style={{ height: '400px' }}>
                        <h3 className="chart-container-title">Power Output & Anomaly Detection</h3>
                        <ResponsiveContainer width="100%" height="85%">
                            <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
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
                                    itemStyle={{ color: 'var(--text-primary)' }}
                                />
                                <Legend />
                                <Area type="monotone" dataKey="power" stroke="var(--accent-primary)" name="Power (W)" fillOpacity={1} fill="url(#colorPower)" />
                                {/* Highlight anomalies magically by showing points where is_anomaly is true */}
                                <Line type="monotone" dataKey="power" stroke="none" dot={(props) => {
                                    const { cx, cy, payload } = props;
                                    if (payload.is_anomaly) {
                                        return <circle cx={cx} cy={cy} r={6} fill="var(--accent-danger)" stroke="white" strokeWidth={2} />;
                                    }
                                    return <span />;
                                }} />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>

                    <div className="glass-card fade-in stagger-3" style={{ height: '350px' }}>
                        <h3 className="chart-container-title">Trend Analysis: Efficiency</h3>
                        <ResponsiveContainer width="100%" height="85%">
                            <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                                <XAxis dataKey="timeLabel" stroke="var(--text-secondary)" tick={{ fontSize: 12 }} />
                                <YAxis stroke="var(--text-secondary)" tick={{ fontSize: 12 }} domain={[0, 100]} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', border: '1px solid var(--border-color)', borderRadius: '8px' }}
                                />
                                <Legend />
                                <Line type="monotone" dataKey="efficiency" stroke="var(--accent-success)" opacity={0.3} dot={false} name="Actual Efficiency %" />
                                <Line type="monotone" dataKey="efficiency_trend" stroke={"var(--accent-success)"} strokeWidth={3} dot={false} name="Trend (Moving Avg)" />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>

                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

                    <div className="glass-card fade-in stagger-3">
                        <h3 className="chart-container-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <Lightbulb color="var(--accent-warning)" />
                            Gen AI Insights (Google Gemini)
                        </h3>
                        {loading ? (
                            <p style={{ color: 'var(--text-secondary)' }}>Analyzing patterns...</p>
                        ) : aiInsight ? (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <span className={`badge ${aiInsight.severity === 'Info' ? 'badge-success' : 'badge-warning'}`}>Severity: {aiInsight.severity}</span>
                                    <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Trend: {aiInsight.trend}</span>
                                </div>
                                <div>
                                    <h4 style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '0.25rem' }}>Insight</h4>
                                    <p style={{ fontWeight: 500 }}>{aiInsight.insight}</p>
                                </div>
                                <div style={{ background: 'rgba(59, 130, 246, 0.1)', padding: '1rem', borderRadius: '8px', borderLeft: '4px solid var(--accent-primary)' }}>
                                    <h4 style={{ color: 'var(--accent-primary)', fontSize: '0.875rem', marginBottom: '0.25rem' }}>Recommended Action</h4>
                                    <p>{aiInsight.recommendation}</p>
                                </div>
                                <button className="btn" onClick={fetchData} style={{ marginTop: '0.5rem' }}>Refresh AI Analysis</button>
                            </div>
                        ) : (
                            <p style={{ color: 'var(--text-secondary)' }}>No insights available.</p>
                        )}
                    </div>

                    <div className="glass-card fade-in stagger-4">
                        <h3 className="chart-container-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <AlertTriangle color="var(--accent-danger)" />
                            System Alerts
                        </h3>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                            {data.filter(d => d.is_anomaly || d.status !== 'Normal').slice(-4).map((alert, i) => (
                                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.75rem', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                        <AlertTriangle size={18} color="var(--accent-danger)" />
                                        <div>
                                            <div style={{ fontWeight: 600 }}>{alert.is_anomaly ? 'Anomaly Detected' : 'System Fault'}</div>
                                            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{alert.timeLabel}</div>
                                        </div>
                                    </div>
                                    <span className="badge badge-danger">High</span>
                                </div>
                            ))}
                            {data.filter(d => d.is_anomaly || d.status !== 'Normal').length === 0 && (
                                <p style={{ color: 'var(--text-secondary)', textAlign: 'center', padding: '1rem 0' }}>All systems operational. No active anomalies.</p>
                            )}
                        </div>
                    </div>

                    <div className="glass-card fade-in stagger-4">
                        <h3 className="chart-container-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <Sun color="var(--accent-warning)" />
                            Environmental Factors
                        </h3>
                        <div style={{ display: 'flex', justifyContent: 'space-between', padding: '1rem 0', borderBottom: '1px solid var(--border-color)' }}>
                            <span style={{ color: 'var(--text-secondary)' }}>Solar Irradiance</span>
                            <span style={{ fontWeight: 600 }}>{latest.solar_irradiance?.toFixed(0) || 0} W/m²</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', padding: '1rem 0', borderBottom: '1px solid var(--border-color)' }}>
                            <span style={{ color: 'var(--text-secondary)' }}>Ambient Temp</span>
                            <span style={{ fontWeight: 600 }}>{latest.ambient_temperature?.toFixed(1) || 0} °C</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', padding: '1rem 0' }}>
                            <span style={{ color: 'var(--text-secondary)' }}>Dust / Soiling Index</span>
                            <span style={{ fontWeight: 600, color: latest.dust_index > 50 ? 'var(--accent-danger)' : 'inherit' }}>{latest.dust_index?.toFixed(0) || 0}%</span>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    );
};

export default Dashboard;
