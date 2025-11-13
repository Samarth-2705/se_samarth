/**
 * Student Dashboard Page
 */
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../utils/AuthContext';
import { studentAPI } from '../services/api';
import { toast } from 'react-toastify';
import './styles.css';

const StudentDashboard = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const response = await studentAPI.getDashboard();
      setDashboardData(response.data);
    } catch (error) {
      toast.error('Failed to load dashboard');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  const { student, statistics, status } = dashboardData || {};

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Admission Automation System</h1>
        <div className="header-actions">
          <span>Welcome, {student?.full_name || user?.email}</span>
          <button onClick={logout} className="btn btn-secondary">
            Logout
          </button>
        </div>
      </header>

      <nav className="dashboard-nav">
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
        <div className="card">
          <h2>Application Status</h2>
          <div className="status-item">
            <span>Current Status:</span>
            <strong>{student?.application_status}</strong>
          </div>
        </div>

        <div className="card">
          <h2>Progress Checklist</h2>
          <div className="checklist">
            <div className={`checklist-item ${status?.registration_complete ? 'completed' : ''}`}>
              <span>✓</span>
              <span>Registration Complete</span>
            </div>
            <div className={`checklist-item ${status?.documents_verified ? 'completed' : ''}`}>
              <span>✓</span>
              <span>Documents Verified</span>
            </div>
            <div className={`checklist-item ${status?.payment_complete ? 'completed' : ''}`}>
              <span>✓</span>
              <span>Payment Complete</span>
            </div>
            <div className={`checklist-item ${status?.choices_submitted ? 'completed' : ''}`}>
              <span>✓</span>
              <span>Choices Submitted</span>
            </div>
            <div className={`checklist-item ${status?.seat_allotted ? 'completed' : ''}`}>
              <span>✓</span>
              <span>Seat Allotted</span>
            </div>
            <div className={`checklist-item ${status?.admission_confirmed ? 'completed' : ''}`}>
              <span>✓</span>
              <span>Admission Confirmed</span>
            </div>
          </div>
        </div>

        <div className="stats-grid">
          <div className="stat-card">
            <h3>Documents</h3>
            <p className="stat-value">{statistics?.documents_uploaded || 0}</p>
            <p className="stat-label">Uploaded</p>
            <p className="stat-value">{statistics?.documents_verified || 0}</p>
            <p className="stat-label">Verified</p>
          </div>

          <div className="stat-card">
            <h3>Choices</h3>
            <p className="stat-value">{statistics?.choices_filled || 0}</p>
            <p className="stat-label">Filled</p>
          </div>

          <div className="stat-card">
            <h3>Payments</h3>
            <p className="stat-value">{statistics?.payments_made || 0}</p>
            <p className="stat-label">Completed</p>
          </div>

          <div className="stat-card">
            <h3>Allotments</h3>
            <p className="stat-value">{statistics?.allotments || 0}</p>
            <p className="stat-label">Received</p>
          </div>
        </div>

        <div className="card">
          <h2>Student Information</h2>
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">Name:</span>
              <span className="info-value">{student?.full_name}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Email:</span>
              <span className="info-value">{user?.email}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Mobile:</span>
              <span className="info-value">{user?.mobile}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Exam Type:</span>
              <span className="info-value">{student?.exam_type}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Rank:</span>
              <span className="info-value">{student?.exam_rank}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Category:</span>
              <span className="info-value">{student?.category}</span>
            </div>
          </div>
        </div>

        <div className="card">
          <h2>Next Steps</h2>
          <ul className="next-steps">
            {!status?.registration_complete && (
              <li>
                <button onClick={() => navigate('/profile')} className="btn btn-link">
                  Complete your profile →
                </button>
              </li>
            )}
            {!status?.documents_verified && (
              <li>
                <button onClick={() => navigate('/documents')} className="btn btn-link">
                  Upload required documents →
                </button>
              </li>
            )}
            {!status?.payment_complete && (
              <li>
                <button onClick={() => navigate('/payment')} className="btn btn-link">
                  Pay application fee →
                </button>
              </li>
            )}
            {!status?.choices_submitted && status?.payment_complete && (
              <li>
                <button onClick={() => navigate('/choices')} className="btn btn-link">
                  Fill your college preferences →
                </button>
              </li>
            )}
            {status?.seat_allotted && !status?.admission_confirmed && (
              <li>
                <button onClick={() => navigate('/allotment')} className="btn btn-link">
                  View and accept your allotted seat →
                </button>
              </li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;
