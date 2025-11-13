import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { adminAPI } from '../services/api';
import { useAuth } from '../utils/AuthContext';
import { toast } from 'react-toastify';
import './styles.css';

const AdminDashboard = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [stats, setStats] = useState(null);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [triggeringAllotment, setTriggeringAllotment] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 10,
    total: 0,
    pages: 0
  });

  useEffect(() => {
    loadDashboard();
    loadStudents();
  }, [pagination.page, statusFilter]);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      const response = await adminAPI.getDashboard();
      setStats(response.data);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  const loadStudents = async () => {
    try {
      const response = await adminAPI.getStudents({
        page: pagination.page,
        per_page: pagination.per_page,
        search: searchTerm,
        status: statusFilter
      });
      setStudents(response.data.students);
      setPagination(response.data.pagination);
    } catch (error) {
      toast.error('Failed to load students');
    }
  };

  const handleTriggerAllotment = async () => {
    const roundNumber = prompt('Enter round number (e.g., 1, 2, 3):');
    if (!roundNumber) return;

    const confirmed = window.confirm(
      `Are you sure you want to trigger seat allotment for Round ${roundNumber}?\n\n` +
      `This will process all eligible students and allot seats based on their choices and ranks.`
    );

    if (!confirmed) return;

    try {
      setTriggeringAllotment(true);
      const response = await adminAPI.triggerAllotment({ round_number: parseInt(roundNumber) });
      toast.success(
        `Seat allotment completed!\n` +
        `Students processed: ${response.data.result.students_processed}\n` +
        `Seats allotted: ${response.data.result.allotments_made}`
      );
      loadDashboard();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to trigger allotment');
    } finally {
      setTriggeringAllotment(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setPagination({ ...pagination, page: 1 });
    loadStudents();
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (loading && !stats) {
    return (
      <div className="dashboard-container">
        <div className="loading">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="admin-header">
        <div>
          <h2>Admin Dashboard</h2>
          <p className="admin-user-info">Logged in as: {user?.email}</p>
        </div>
        <div className="admin-actions">
          <button
            onClick={handleTriggerAllotment}
            disabled={triggeringAllotment}
            className="btn btn-primary"
          >
            {triggeringAllotment ? 'Processing...' : 'Trigger Seat Allotment'}
          </button>
          <button onClick={handleLogout} className="btn btn-secondary">
            Logout
          </button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="stats-grid">
        {/* Student Statistics */}
        <div className="stat-card">
          <h3>Students</h3>
          <div className="stat-items">
            <div className="stat-item">
              <span className="stat-label">Total Students</span>
              <span className="stat-value">{stats?.students?.total || 0}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Registrations Complete</span>
              <span className="stat-value">{stats?.students?.registrations_complete || 0}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Documents Verified</span>
              <span className="stat-value">{stats?.students?.documents_verified || 0}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Payments Complete</span>
              <span className="stat-value">{stats?.students?.payments_complete || 0}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Choices Submitted</span>
              <span className="stat-value">{stats?.students?.choices_submitted || 0}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Seats Allotted</span>
              <span className="stat-value highlight">{stats?.students?.seats_allotted || 0}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Admissions Confirmed</span>
              <span className="stat-value highlight">{stats?.students?.admissions_confirmed || 0}</span>
            </div>
          </div>
        </div>

        {/* Financial Statistics */}
        <div className="stat-card">
          <h3>Financial</h3>
          <div className="stat-items">
            <div className="stat-item">
              <span className="stat-label">Total Revenue</span>
              <span className="stat-value">₹{stats?.financial?.total_revenue?.toLocaleString() || 0}</span>
            </div>
          </div>
        </div>

        {/* Document Statistics */}
        <div className="stat-card">
          <h3>Documents</h3>
          <div className="stat-items">
            <div className="stat-item">
              <span className="stat-label">Pending Verification</span>
              <span className="stat-value">{stats?.documents?.pending_verification || 0}</span>
            </div>
          </div>
        </div>

        {/* Infrastructure Statistics */}
        <div className="stat-card">
          <h3>Infrastructure</h3>
          <div className="stat-items">
            <div className="stat-item">
              <span className="stat-label">Total Colleges</span>
              <span className="stat-value">{stats?.infrastructure?.total_colleges || 0}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Total Courses</span>
              <span className="stat-value">{stats?.infrastructure?.total_courses || 0}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Total Seats</span>
              <span className="stat-value">{stats?.infrastructure?.total_seats || 0}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Available Seats</span>
              <span className="stat-value">{stats?.infrastructure?.available_seats || 0}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Seats Filled</span>
              <span className="stat-value">{stats?.infrastructure?.seats_filled || 0}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Student List */}
      <div className="student-list-section">
        <h3>Student Management</h3>

        {/* Search and Filter */}
        <div className="search-filter-bar">
          <form onSubmit={handleSearch} className="search-form">
            <input
              type="text"
              placeholder="Search by name, email, or roll number..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
            <button type="submit" className="btn btn-secondary">Search</button>
          </form>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="filter-select"
          >
            <option value="">All Students</option>
            <option value="registered">Registered</option>
            <option value="verified">Documents Verified</option>
            <option value="paid">Payment Complete</option>
            <option value="allotted">Seat Allotted</option>
          </select>
        </div>

        {/* Student Table */}
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Rank</th>
                <th>Category</th>
                <th>Status</th>
                <th>Payment</th>
                <th>Documents</th>
                <th>Choices</th>
                <th>Seat</th>
              </tr>
            </thead>
            <tbody>
              {students.length === 0 ? (
                <tr>
                  <td colSpan="9" className="text-center">No students found</td>
                </tr>
              ) : (
                students.map(student => (
                  <tr key={student.id}>
                    <td>{student.full_name}</td>
                    <td>{student.user?.email}</td>
                    <td>{student.exam_rank}</td>
                    <td>{student.category}</td>
                    <td>
                      <span className={`badge ${student.registration_complete ? 'badge-success' : 'badge-warning'}`}>
                        {student.registration_complete ? 'Complete' : 'Incomplete'}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${student.payment_complete ? 'badge-success' : 'badge-warning'}`}>
                        {student.payment_complete ? 'Paid' : 'Pending'}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${student.documents_verified ? 'badge-success' : 'badge-warning'}`}>
                        {student.documents_verified ? 'Verified' : 'Pending'}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${student.choices_submitted ? 'badge-success' : 'badge-warning'}`}>
                        {student.choices_submitted ? 'Submitted' : 'Pending'}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${student.seat_allotted ? 'badge-success' : 'badge-secondary'}`}>
                        {student.seat_allotted ? 'Allotted' : 'Not Allotted'}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {pagination.pages > 1 && (
          <div className="pagination">
            <button
              onClick={() => setPagination({ ...pagination, page: pagination.page - 1 })}
              disabled={!pagination.has_prev}
              className="btn btn-secondary"
            >
              Previous
            </button>
            <span className="pagination-info">
              Page {pagination.page} of {pagination.pages} ({pagination.total} students)
            </span>
            <button
              onClick={() => setPagination({ ...pagination, page: pagination.page + 1 })}
              disabled={!pagination.has_next}
              className="btn btn-secondary"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;
