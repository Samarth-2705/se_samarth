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
  const [processing, setProcessing] = useState(false);

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
    if (processing) return;

    // Check if this payment type already exists
    const existingPayment = payments.find(
      p => p.payment_type === paymentType && p.status === 'success'
    );

    if (existingPayment) {
      toast.warning('This payment has already been completed');
      return;
    }

    const confirmPayment = window.confirm(
      `Are you sure you want to make a payment of ₹${amount} for ${paymentType.replace(/_/g, ' ')}?`
    );

    if (!confirmPayment) return;

    setProcessing(true);

    try {
      // Create payment order
      const orderResponse = await paymentAPI.createOrder({
        amount: amount,
        payment_type: paymentType
      });

      if (!orderResponse.data || !orderResponse.data.order) {
        throw new Error('Failed to create payment order');
      }

      const order = orderResponse.data.order;

      // Simulate payment success (in production, this would be handled by Razorpay)
      // For demo purposes, we'll auto-verify the payment
      toast.info('Processing payment... Please wait');

      // Simulate payment processing delay
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Verify payment (this simulates a successful Razorpay payment)
      const verifyResponse = await paymentAPI.verify({
        payment_id: order.id,
        razorpay_payment_id: `test_pay_${Date.now()}`,
        razorpay_signature: `test_sig_${Date.now()}`
      });

      toast.success('Payment completed successfully!');
      loadPaymentHistory();

    } catch (error) {
      console.error('Payment error:', error);
      toast.error(error.response?.data?.error || 'Payment failed. Please try again.');
    } finally {
      setProcessing(false);
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

  const hasCompletedPayment = (type) => {
    return payments.some(p => p.payment_type === type && p.status === 'success');
  };

  return (
    <Layout title="Payments">
      <div className="card">
        <h3>Make Payment</h3>
        <p className="text-muted">
          <strong>Note:</strong> This is a demo payment system. In production, payments would be processed through Razorpay.
        </p>
        <div className="payment-options">
          <div className="payment-card">
            <h4>Application Fee</h4>
            <p className="payment-amount">₹500</p>
            <p className="payment-desc">One-time application processing fee</p>
            {hasCompletedPayment('application_fee') ? (
              <button className="btn btn-success" disabled>
                ✓ Paid
              </button>
            ) : (
              <button
                onClick={() => handlePayment('application_fee', 500)}
                className="btn btn-primary"
                disabled={processing}
              >
                {processing ? 'Processing...' : 'Pay Now'}
              </button>
            )}
          </div>
          <div className="payment-card">
            <h4>Counselling Fee</h4>
            <p className="payment-amount">₹1000</p>
            <p className="payment-desc">Seat allotment counselling fee</p>
            {hasCompletedPayment('counselling_fee') ? (
              <button className="btn btn-success" disabled>
                ✓ Paid
              </button>
            ) : (
              <button
                onClick={() => handlePayment('counselling_fee', 1000)}
                className="btn btn-primary"
                disabled={processing}
              >
                {processing ? 'Processing...' : 'Pay Now'}
              </button>
            )}
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
                    <td>{payment.payment_method || 'Test Mode'}</td>
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
          <li><strong>Demo Mode:</strong> Payments are simulated for testing purposes</li>
        </ul>
      </div>
    </Layout>
  );
};

export default Payment;
