/**
 * Choice Filling Page
 */
import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import Layout from '../components/Layout';
import { choiceAPI } from '../services/api';
import './styles.css';

const ChoiceFilling = () => {
  const [choices, setChoices] = useState([]);
  const [colleges, setColleges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitted, setSubmitted] = useState(false);
  const [adding, setAdding] = useState(null); // Track which course is being added

  useEffect(() => {
    loadChoices();
    loadEligibleColleges();
  }, []);

  const loadChoices = async () => {
    try {
      const response = await choiceAPI.list();
      setChoices(response.data.choices || []);
      setSubmitted(response.data.submitted || false);
    } catch (error) {
      toast.error('Failed to load choices');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const loadEligibleColleges = async () => {
    try {
      const response = await choiceAPI.getEligibleColleges();
      setColleges(response.data.eligible_colleges || []);
    } catch (error) {
      console.error('Failed to load eligible colleges:', error);
    }
  };

  const handleAddChoice = async (courseId) => {
    if (adding) return; // Prevent multiple simultaneous additions

    setAdding(courseId);

    try {
      await choiceAPI.add({ course_id: courseId });
      toast.success('Choice added successfully');
      await loadChoices(); // Reload choices to get updated list
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to add choice');
      console.error(error);
    } finally {
      setAdding(null);
    }
  };

  const handleRemoveChoice = async (choiceId) => {
    if (window.confirm('Are you sure you want to remove this choice?')) {
      try {
        await choiceAPI.remove(choiceId);
        toast.success('Choice removed successfully');
        await loadChoices(); // Reload choices to get updated list
      } catch (error) {
        toast.error(error.response?.data?.error || 'Failed to remove choice');
        console.error(error);
      }
    }
  };

  const handleSubmitChoices = async () => {
    if (choices.length === 0) {
      toast.error('Please add at least one choice before submitting');
      return;
    }

    if (window.confirm('Are you sure you want to submit your choices? They cannot be modified after submission.')) {
      try {
        await choiceAPI.submit();
        toast.success('Choices submitted successfully');
        loadChoices();
      } catch (error) {
        toast.error(error.response?.data?.error || 'Failed to submit choices');
        console.error(error);
      }
    }
  };

  const isChoiceAdded = (courseId) => {
    return choices.some(choice => choice.course_id === courseId);
  };

  return (
    <Layout title="Choice Filling">
      <div className="card">
        <div className="card-header">
          <h3>My Choices {submitted && <span className="badge badge-success">Submitted</span>}</h3>
          {!submitted && choices.length > 0 && (
            <button onClick={handleSubmitChoices} className="btn btn-primary">
              Submit Choices ({choices.length} selected)
            </button>
          )}
        </div>

        {loading ? (
          <div className="loading">Loading choices...</div>
        ) : choices.length === 0 ? (
          <div className="no-data">
            <p>No choices added yet</p>
            <p className="text-muted">Add colleges from the eligible colleges list below</p>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="table">
              <thead>
                <tr>
                  <th>Preference</th>
                  <th>College</th>
                  <th>Course</th>
                  <th>Location</th>
                  <th>Available Seats</th>
                  {!submitted && <th>Actions</th>}
                </tr>
              </thead>
              <tbody>
                {choices.map((choice) => (
                  <tr key={choice.id}>
                    <td>#{choice.preference_order}</td>
                    <td>{choice.college?.name}</td>
                    <td>{choice.course?.name}</td>
                    <td>{choice.college?.city}, {choice.college?.state}</td>
                    <td>{choice.course?.available_seats}</td>
                    {!submitted && (
                      <td>
                        <button
                          onClick={() => handleRemoveChoice(choice.id)}
                          className="btn btn-sm btn-danger"
                        >
                          Remove
                        </button>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {!submitted && (
        <div className="card">
          <h3>Eligible Colleges</h3>
          {colleges.length === 0 ? (
            <div className="no-data">
              <p>No eligible colleges found based on your rank (1500)</p>
              <p className="text-muted">Please contact admin if you believe this is an error</p>
            </div>
          ) : (
            <div className="colleges-grid">
              {colleges.map((collegeData) => (
                <div key={collegeData.college.id} className="college-card">
                  <h4>{collegeData.college.name}</h4>
                  <p className="college-location">
                    📍 {collegeData.college.city}, {collegeData.college.state}
                  </p>
                  <p className="college-type">
                    <span className="badge badge-info">{collegeData.college.type}</span>
                    <span className="badge badge-secondary">{collegeData.college.affiliation}</span>
                  </p>
                  <div className="courses-list">
                    <strong>Available Courses:</strong>
                    <ul>
                      {collegeData.courses.map((course) => {
                        const alreadyAdded = isChoiceAdded(course.id);
                        return (
                          <li key={course.id}>
                            <div className="course-info">
                              <span className="course-name">{course.name}</span>
                              <span className="course-details">
                                {course.available_seats} seats • ₹{course.fee_per_year?.toLocaleString()}/year
                              </span>
                              <span className="course-rank">
                                Rank: {course.min_rank} - {course.max_rank}
                              </span>
                            </div>
                            {alreadyAdded ? (
                              <button className="btn btn-sm btn-success" disabled>
                                ✓ Added
                              </button>
                            ) : (
                              <button
                                onClick={() => handleAddChoice(course.id)}
                                className="btn btn-sm btn-primary"
                                disabled={adding === course.id}
                              >
                                {adding === course.id ? 'Adding...' : 'Add to Choices'}
                              </button>
                            )}
                          </li>
                        );
                      })}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <div className="card">
        <h3>Important Information</h3>
        <ul className="info-list">
          <li>You can add up to 100 choices in order of preference</li>
          <li>Choices are automatically ordered based on when you add them</li>
          <li>Once submitted, choices cannot be modified</li>
          <li>Seat allotment will be based on your rank and choice preference</li>
          <li>Higher preference choices (lower numbers) will be considered first</li>
          <li>Make sure to review all your choices before submitting</li>
        </ul>
      </div>
    </Layout>
  );
};

export default ChoiceFilling;
