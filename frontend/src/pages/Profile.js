/**
 * Student Profile Page
 */
import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import Layout from '../components/Layout';
import { studentAPI } from '../services/api';
import './styles.css';

const Profile = () => {
  const [profile, setProfile] = useState(null);
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    address_line1: '',
    address_line2: '',
    city: '',
    state: '',
    pincode: '',
    guardian_name: '',
    guardian_mobile: '',
    guardian_email: ''
  });

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const response = await studentAPI.getProfile();
      setProfile(response.data);
      setFormData({
        address_line1: response.data.address_line1 || '',
        address_line2: response.data.address_line2 || '',
        city: response.data.city || '',
        state: response.data.state || '',
        pincode: response.data.pincode || '',
        guardian_name: response.data.guardian_name || '',
        guardian_mobile: response.data.guardian_mobile || '',
        guardian_email: response.data.guardian_email || ''
      });
    } catch (error) {
      toast.error('Failed to load profile');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await studentAPI.updateProfile(formData);
      toast.success('Profile updated successfully');
      setEditing(false);
      loadProfile();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to update profile');
      console.error(error);
    }
  };

  if (loading) {
    return (
      <Layout title="Profile">
        <div className="loading">Loading profile...</div>
      </Layout>
    );
  }

  return (
    <Layout title="Student Profile">
      <div className="card">
        <div className="card-header">
          <h3>Personal Information</h3>
          {!editing && (
            <button onClick={() => setEditing(true)} className="btn btn-primary">
              Edit Profile
            </button>
          )}
        </div>

        {!editing ? (
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">Full Name:</span>
              <span className="info-value">{profile?.full_name}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Email:</span>
              <span className="info-value">{profile?.user?.email}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Mobile:</span>
              <span className="info-value">{profile?.user?.mobile}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Date of Birth:</span>
              <span className="info-value">{profile?.date_of_birth}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Gender:</span>
              <span className="info-value">{profile?.gender}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Category:</span>
              <span className="info-value">{profile?.category}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Exam Type:</span>
              <span className="info-value">{profile?.exam_type}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Exam Rank:</span>
              <span className="info-value">{profile?.exam_rank}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Exam Roll Number:</span>
              <span className="info-value">{profile?.exam_roll_number}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Address:</span>
              <span className="info-value">
                {profile?.address_line1 && `${profile.address_line1}, `}
                {profile?.address_line2 && `${profile.address_line2}, `}
                {profile?.city && `${profile.city}, `}
                {profile?.state && `${profile.state} - `}
                {profile?.pincode}
              </span>
            </div>
            <div className="info-item">
              <span className="info-label">Guardian Name:</span>
              <span className="info-value">{profile?.guardian_name || 'Not provided'}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Guardian Mobile:</span>
              <span className="info-value">{profile?.guardian_mobile || 'Not provided'}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Guardian Email:</span>
              <span className="info-value">{profile?.guardian_email || 'Not provided'}</span>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="profile-form">
            <div className="form-group">
              <label>Address Line 1 *</label>
              <input
                type="text"
                name="address_line1"
                value={formData.address_line1}
                onChange={handleChange}
                className="form-control"
                required
              />
            </div>
            <div className="form-group">
              <label>Address Line 2</label>
              <input
                type="text"
                name="address_line2"
                value={formData.address_line2}
                onChange={handleChange}
                className="form-control"
              />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>City *</label>
                <input
                  type="text"
                  name="city"
                  value={formData.city}
                  onChange={handleChange}
                  className="form-control"
                  required
                />
              </div>
              <div className="form-group">
                <label>State *</label>
                <input
                  type="text"
                  name="state"
                  value={formData.state}
                  onChange={handleChange}
                  className="form-control"
                  required
                />
              </div>
              <div className="form-group">
                <label>Pincode *</label>
                <input
                  type="text"
                  name="pincode"
                  value={formData.pincode}
                  onChange={handleChange}
                  className="form-control"
                  pattern="[0-9]{6}"
                  required
                />
              </div>
            </div>
            <div className="form-group">
              <label>Guardian Name *</label>
              <input
                type="text"
                name="guardian_name"
                value={formData.guardian_name}
                onChange={handleChange}
                className="form-control"
                required
              />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Guardian Mobile *</label>
                <input
                  type="tel"
                  name="guardian_mobile"
                  value={formData.guardian_mobile}
                  onChange={handleChange}
                  className="form-control"
                  pattern="[0-9]{10}"
                  required
                />
              </div>
              <div className="form-group">
                <label>Guardian Email</label>
                <input
                  type="email"
                  name="guardian_email"
                  value={formData.guardian_email}
                  onChange={handleChange}
                  className="form-control"
                />
              </div>
            </div>
            <div className="form-actions">
              <button type="submit" className="btn btn-primary">
                Save Changes
              </button>
              <button type="button" onClick={() => setEditing(false)} className="btn btn-secondary">
                Cancel
              </button>
            </div>
          </form>
        )}
      </div>
    </Layout>
  );
};

export default Profile;
