/**
 * Documents Page
 */
import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import Layout from '../components/Layout';
import { documentAPI } from '../services/api';
import './styles.css';

const Documents = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [documentType, setDocumentType] = useState('');

  const documentTypes = [
    { value: 'marks_card_10th', label: '10th Marks Card' },
    { value: 'marks_card_12th', label: '12th Marks Card' },
    { value: 'rank_card', label: 'Rank Card' },
    { value: 'income_certificate', label: 'Income Certificate' },
    { value: 'caste_certificate', label: 'Caste Certificate' },
    { value: 'domicile_certificate', label: 'Domicile Certificate' },
    { value: 'pwd_certificate', label: 'PWD Certificate' },
    { value: 'other', label: 'Other' }
  ];

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const response = await documentAPI.list();
      setDocuments(response.data.documents || []);
    } catch (error) {
      toast.error('Failed to load documents');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  const handleUpload = async (e) => {
    e.preventDefault();

    if (!selectedFile || !documentType) {
      toast.error('Please select a file and document type');
      return;
    }

    setUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('document_type', documentType);

      await documentAPI.upload(formData);
      toast.success('Document uploaded successfully');
      setSelectedFile(null);
      setDocumentType('');
      e.target.reset();
      loadDocuments();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to upload document');
      console.error(error);
    } finally {
      setUploading(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusColors = {
      'pending': 'badge-warning',
      'verified': 'badge-success',
      'rejected': 'badge-danger'
    };
    return <span className={`badge ${statusColors[status] || 'badge-secondary'}`}>{status}</span>;
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  return (
    <Layout title="Documents">
      <div className="card">
        <h3>Upload Document</h3>
        <form onSubmit={handleUpload} className="upload-form">
          <div className="form-row">
            <div className="form-group">
              <label>Document Type *</label>
              <select
                value={documentType}
                onChange={(e) => setDocumentType(e.target.value)}
                className="form-control"
                required
              >
                <option value="">Select document type</option>
                {documentTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Select File * (PDF, JPG, PNG - Max 5MB)</label>
              <input
                type="file"
                onChange={handleFileChange}
                className="form-control"
                accept=".pdf,.jpg,.jpeg,.png"
                required
              />
            </div>
          </div>
          <button type="submit" className="btn btn-primary" disabled={uploading}>
            {uploading ? 'Uploading...' : 'Upload Document'}
          </button>
        </form>
      </div>

      <div className="card">
        <h3>Uploaded Documents</h3>
        {loading ? (
          <div className="loading">Loading documents...</div>
        ) : documents.length === 0 ? (
          <p className="no-data">No documents uploaded yet</p>
        ) : (
          <div className="table-responsive">
            <table className="table">
              <thead>
                <tr>
                  <th>Document Type</th>
                  <th>File Name</th>
                  <th>Size</th>
                  <th>Uploaded At</th>
                  <th>Status</th>
                  <th>Remarks</th>
                </tr>
              </thead>
              <tbody>
                {documents.map((doc) => (
                  <tr key={doc.id}>
                    <td>{doc.document_type?.replace(/_/g, ' ').toUpperCase()}</td>
                    <td>{doc.file_name}</td>
                    <td>{formatFileSize(doc.file_size)}</td>
                    <td>{new Date(doc.uploaded_at).toLocaleString()}</td>
                    <td>{getStatusBadge(doc.status)}</td>
                    <td>
                      {doc.status === 'rejected' && doc.rejection_reason ? (
                        <span className="text-danger">{doc.rejection_reason}</span>
                      ) : doc.status === 'verified' ? (
                        <span className="text-success">Verified</span>
                      ) : (
                        <span className="text-muted">Under review</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="card">
        <h3>Required Documents</h3>
        <ul className="document-checklist">
          <li>✓ 10th Standard Marks Card</li>
          <li>✓ 12th Standard Marks Card</li>
          <li>✓ Entrance Exam Rank Card</li>
          <li>Optional: Income Certificate (for fee concession)</li>
          <li>Optional: Caste Certificate (if applicable)</li>
          <li>Optional: Domicile Certificate</li>
          <li>Optional: PWD Certificate (if applicable)</li>
        </ul>
      </div>
    </Layout>
  );
};

export default Documents;
