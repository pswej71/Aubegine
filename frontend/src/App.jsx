import React from 'react';
import Dashboard from './components/Dashboard';
import './App.css'; // Remove default vite App.css completely from index.html if possible or keep empty

function App() {
  return (
    <div>
      <nav className="top-nav fade-in">
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ width: 28, height: 28, borderRadius: 8, background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))' }}></div>
          <h1 className="gradient-text" style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0 }}>SolarSync Analytics</h1>
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <span className="badge badge-success">System Online</span>
          <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', fontWeight: 500 }}>Site: Alpha Station</span>
        </div>
      </nav>
      <main className="main-content">
        <Dashboard />
      </main>
    </div>
  );
}

export default App;
