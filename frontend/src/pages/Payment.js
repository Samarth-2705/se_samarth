/**
 * Payment Page
 */
import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import Layout from '../components/Layout';
import { paymentAPI } from '../services/api';
import './styles.css';

const Payment = () => {
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPaymentHistory();
  }, []);

  const loadPaymentHistory = async () => {
    try {
      const response = await paymentAPI.getHistory();
      setPayments(response.data.payments || []);
    } catch (error) {
      toast.error('Failed to load payment history');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handlePayment = async (paymentType, amount) => {
    try {
      toast.info('Payment feature is under development');
      // Payment integration will be added here
      /*
      const response = await paymentAPI.createOrder({
        amount: amount,
        payment_type: paymentType
      });
      // Razorpay integration code here
      */
    } catch (error) {
      toast.error('Failed to initiate payment');
      console.error(error);
    }
  };

  const getStatusBadge = (status) => {
    const statusColors = {
      'success': 'badge-success',
      'pending': 'badge-warning',
      'failed': 'badge-danger',
      'refunded': 'badge-info'
    };
    return <span className={`badge ${statusColors[status] || 'badge-secondary'}`}>{status}</span>;
  };

  return (
    <Layout title="Payments">
      <div className="card">
        <h3>Make Payment</h3>
        <div className="payment-options">
          <div className="payment-card">
            <h4>Application Fee</h4>
            <p className="payment-amount">₹500</p>
            <p className="payment-desc">One-time application processing fee</p>
            <button
              onClick={() => handlePayment('application_fee', 500)}
              className="btn btn-primary"
            >
              Pay Now
            </button>
          </div>
          <div className="payment-card">
            <h4>Counselling Fee</h4>
            <p className="payment-amount">₹1000</p>
            <p className="payment-desc">Seat allotment counselling fee</p>
            <button
              onClick={() => handlePayment('counselling_fee', 1000)}
              className="btn btn-primary"
            >
              Pay Now
            </button>
          </div>
        </div>
      </div>

      <div className="card">
        <h3>Payment History</h3>
        {loading ? (
          <div className="loading">Loading payment history...</div>
        ) : payments.length === 0 ? (
          <p className="no-data">No payments made yet</p>
        ) : (
          <div className="table-responsive">
            <table className="table">
              <thead>
                <tr>
                  <th>Payment ID</th>
                  <th>Type</th>
                  <th>Amount</th>
                  <th>Date</th>
                  <th>Status</th>
                  <th>Payment Method</th>
                </tr>
              </thead>
              <tbody>
                {payments.map((payment) => (
                  <tr key={payment.id}>
                    <td>{payment.order_id}</td>
                    <td>{payment.payment_type?.replace(/_/g, ' ').toUpperCase()}</td>
                    <td>₹{payment.amount}</td>
                    <td>{new Date(payment.initiated_at).toLocaleString()}</td>
                    <td>{getStatusBadge(payment.status)}</td>
                    <td>{payment.payment_method || 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="card">
        <h3>Payment Information</h3>
        <ul className="info-list">
          <li>All payments are processed securely through Razorpay</li>
          <li>Application fee is non-refundable</li>
          <li>Counselling fee may be refunded as per university rules</li>
          <li>Keep your payment receipt for future reference</li>
        </ul>
      </div>
    </Layout>
  );
};

export default Payment;
