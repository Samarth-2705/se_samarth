/**
 * Seat Allotment Page
 */
import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import Layout from '../components/Layout';
import { allotmentAPI } from '../services/api';
import './styles.css';

const SeatAllotment = () => {
  const [allotment, setAllotment] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAllotment();
  }, []);

  const loadAllotment = async () => {
    try {
      const response = await allotmentAPI.getMyAllotment();
      setAllotment(response.data.allotment);
    } catch (error) {
      toast.error('Failed to load allotment');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptSeat = async (freeze) => {
    if (!allotment) return;

    const message = freeze
      ? 'Are you sure you want to freeze this seat? You will not be eligible for upgrades.'
      : 'Are you sure you want to accept this seat? You can still upgrade in next rounds.';

    if (window.confirm(message)) {
      try {
        await allotmentAPI.accept(allotment.id, freeze);
        toast.success('Seat accepted successfully');
        loadAllotment();
      } catch (error) {
        toast.error(error.response?.data?.error || 'Failed to accept seat');
        console.error(error);
      }
    }
  };

  const handleRejectSeat = async () => {
    if (!allotment) return;

    const reason = prompt('Please provide a reason for rejecting this seat:');
    if (!reason) return;

    try {
      await allotmentAPI.reject(allotment.id, reason);
      toast.success('Seat rejected');
      loadAllotment();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to reject seat');
      console.error(error);
    }
  };

  const getStatusBadge = (status) => {
    const statusColors = {
      'allotted': 'badge-info',
      'accepted_frozen': 'badge-success',
      'accepted_upgrade': 'badge-warning',
      'rejected': 'badge-danger'
    };
    return <span className={`badge ${statusColors[status] || 'badge-secondary'}`}>{status?.replace(/_/g, ' ')}</span>;
  };

  return (
    <Layout title="Seat Allotment">
      {loading ? (
        <div className="loading">Loading allotment details...</div>
      ) : !allotment ? (
        <div className="card">
          <h3>No Seat Allotted</h3>
          <p>You have not been allotted any seat yet. Please wait for the allotment process to complete.</p>
          <div className="allotment-info">
            <h4>Allotment Schedule</h4>
            <ul>
              <li>Round 1: Results will be announced soon</li>
              <li>Round 2: After Round 1 acceptance</li>
              <li>Round 3: Final round</li>
            </ul>
          </div>
        </div>
      ) : (
        <>
          <div className="card">
            <div className="card-header">
              <h3>Seat Allotment Details</h3>
              {getStatusBadge(allotment.status)}
            </div>

            <div className="allotment-details">
              <div className="info-grid">
                <div className="info-item">
                  <span className="info-label">College:</span>
                  <span className="info-value">{allotment.college?.name}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Course:</span>
                  <span className="info-value">{allotment.course?.name}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Location:</span>
                  <span className="info-value">{allotment.college?.city}, {allotment.college?.state}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Allotment Round:</span>
                  <span className="info-value">Round {allotment.round?.round_number}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Category:</span>
                  <span className="info-value">{allotment.category}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Allotted On:</span>
                  <span className="info-value">{new Date(allotment.allotted_at).toLocaleDateString()}</span>
                </div>
              </div>
            </div>

            {allotment.status === 'allotted' && (
              <div className="allotment-actions">
                <h4>Accept or Reject Seat</h4>
                <p className="text-muted">You must respond to this allotment within the deadline</p>
                <div className="action-buttons">
                  <button
                    onClick={() => handleAcceptSeat(true)}
                    className="btn btn-success"
                  >
                    Accept & Freeze (No Upgrades)
                  </button>
                  <button
                    onClick={() => handleAcceptSeat(false)}
                    className="btn btn-primary"
                  >
                    Accept & Allow Upgrade
                  </button>
                  <button
                    onClick={handleRejectSeat}
                    className="btn btn-danger"
                  >
                    Reject Seat
                  </button>
                </div>
              </div>
            )}

            {allotment.status === 'accepted_frozen' && (
              <div className="status-message success">
                You have accepted and frozen this seat. No further upgrades will be considered.
              </div>
            )}

            {allotment.status === 'accepted_upgrade' && (
              <div className="status-message info">
                You have accepted this seat but opted for upgrades. You may get a better seat in next rounds.
              </div>
            )}
          </div>

          <div className="card">
            <h3>Next Steps</h3>
            <ul className="info-list">
              <li>Pay the admission fee before the deadline to confirm your seat</li>
              <li>Download and submit the required documents to the college</li>
              <li>Visit the college for verification and final admission</li>
              <li>Keep checking for further notifications and updates</li>
            </ul>
          </div>
        </>
      )}
    </Layout>
  );
};

export default SeatAllotment;
