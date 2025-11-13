/**
 * Shared Layout Component
 */
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../utils/AuthContext';

const Layout = ({ children, title }) => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Admission Automation System</h1>
        <div className="header-actions">
          <span>Welcome, {user?.email}</span>
          <button onClick={logout} className="btn btn-secondary">
            Logout
          </button>
        </div>
      </header>

      <nav className="dashboard-nav">
        <button onClick={() => navigate('/dashboard')} className="nav-btn">
          Dashboard
        </button>
        <button onClick={() => navigate('/profile')} className="nav-btn">
          Profile
        </button>
        <button onClick={() => navigate('/documents')} className="nav-btn">
          Documents
        </button>
        <button onClick={() => navigate('/payment')} className="nav-btn">
          Payment
        </button>
        <button onClick={() => navigate('/choices')} className="nav-btn">
          Choice Filling
        </button>
        <button onClick={() => navigate('/allotment')} className="nav-btn">
          Seat Allotment
        </button>
      </nav>

      <div className="dashboard-content">
        {title && (
          <div className="page-title">
            <h2>{title}</h2>
          </div>
        )}
        {children}
      </div>
    </div>
  );
};

export default Layout;
