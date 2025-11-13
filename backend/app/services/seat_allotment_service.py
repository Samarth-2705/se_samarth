"""
Seat Allotment Service - Core algorithm for automated seat allocation
"""
from flask import current_app
from datetime import datetime, timedelta
from sqlalchemy import and_
from app.models import (
    db, Student, Choice, Course, Allotment, AllotmentRound,
    AllotmentStatus
)
from app.services.email_service import EmailService
from app.services.sms_service import SMSService


class SeatAllotmentService:
    """Service for automated seat allotment"""

    @staticmethod
    def create_allotment_round(round_number, start_date, end_date, acceptance_deadline):
        """
        Create a new allotment round

        Args:
            round_number: Round number (1, 2, 3, etc.)
            start_date: Start date of the round
            end_date: End date of the round
            acceptance_deadline: Deadline for seat acceptance

        Returns:
            AllotmentRound: Created round or None
        """
        try:
            # Check if round already exists
            existing_round = AllotmentRound.query.filter_by(round_number=round_number).first()
            if existing_round:
                current_app.logger.warning(f"Round {round_number} already exists")
                return existing_round

            # Create new round
            allotment_round = AllotmentRound(
                round_number=round_number,
                start_date=start_date,
                end_date=end_date,
                acceptance_deadline=acceptance_deadline,
                is_active=True,
                is_completed=False
            )

            db.session.add(allotment_round)
            db.session.commit()

            current_app.logger.info(f"Created allotment round {round_number}")
            return allotment_round

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to create allotment round: {str(e)}")
            return None

    @staticmethod
    def run_seat_allotment(round_id):
        """
        Run the seat allotment algorithm for a round

        Args:
            round_id: Allotment round ID

        Returns:
            dict: Statistics about the allotment
        """
        try:
            allotment_round = AllotmentRound.query.get(round_id)
            if not allotment_round:
                return {'error': 'Round not found'}

            current_app.logger.info(f"Starting seat allotment for round {allotment_round.round_number}")

            # Get all eligible students who have submitted choices
            eligible_students = Student.query.filter(
                and_(
                    Student.choices_submitted == True,
                    Student.payment_complete == True,
                    Student.documents_verified == True
                )
            ).order_by(Student.exam_rank).all()

            current_app.logger.info(f"Found {len(eligible_students)} eligible students")

            allotments_made = 0
            students_processed = 0

            # Process each student in rank order
            for student in eligible_students:
                students_processed += 1

                # Skip if student already has a frozen seat in this round
                existing_allotment = Allotment.query.filter_by(
                    student_id=student.id,
                    round_id=round_id
                ).first()

                if existing_allotment and existing_allotment.status == AllotmentStatus.ACCEPTED_FROZEN:
                    current_app.logger.info(f"Student {student.id} already has frozen seat")
                    continue

                # Check if student had a seat in previous round
                if allotment_round.round_number > 1:
                    previous_allotment = Allotment.query.filter_by(
                        student_id=student.id,
                        round_id=round_id - 1
                    ).first()

                    # Skip if student froze their seat in previous round
                    if previous_allotment and previous_allotment.status == AllotmentStatus.ACCEPTED_FROZEN:
                        current_app.logger.info(f"Student {student.id} froze seat in previous round")
                        continue

                # Get student's choices in preference order
                choices = Choice.query.filter_by(
                    student_id=student.id,
                    is_locked=True
                ).order_by(Choice.preference_order).all()

                if not choices:
                    current_app.logger.warning(f"Student {student.id} has no choices")
                    continue

                # Try to allot a seat based on preferences
                seat_allotted = False
                for choice in choices:
                    course = choice.course

                    # Check if course is active
                    if not course.is_active:
                        continue

                    # Check seat availability
                    if course.available_seats <= 0:
                        continue

                    # Check category-wise seat availability
                    category_seat_available = SeatAllotmentService._check_category_seat(
                        course, student.category
                    )

                    if not category_seat_available:
                        continue

                    # Check rank eligibility
                    if course.min_rank and student.exam_rank < course.min_rank:
                        continue
                    if course.max_rank and student.exam_rank > course.max_rank:
                        continue

                    # Allot the seat
                    allotment = Allotment(
                        student_id=student.id,
                        course_id=course.id,
                        round_id=round_id,
                        allotted_rank=student.exam_rank,
                        allotted_category=student.category,
                        status=AllotmentStatus.ALLOTTED
                    )

                    # Reduce available seats
                    course.available_seats -= 1
                    SeatAllotmentService._reduce_category_seat(course, student.category)

                    # Update student status
                    student.seat_allotted = True

                    db.session.add(allotment)
                    allotments_made += 1
                    seat_allotted = True

                    current_app.logger.info(
                        f"Allotted seat to student {student.id} - Course {course.id} - Rank {student.exam_rank}"
                    )

                    # Send notification
                    if student.user:
                        EmailService.send_seat_allotment_notification(
                            student.user.email,
                            student.full_name,
                            course.college.name,
                            course.name,
                            allotment_round.round_number,
                            student.user_id
                        )
                        SMSService.send_seat_allotment_sms(
                            student.user.mobile,
                            student.full_name,
                            course.college.name,
                            student.user_id
                        )

                    break  # Stop after first successful allotment

            # Update round statistics
            allotment_round.total_allotments = allotments_made
            allotment_round.is_completed = True

            db.session.commit()

            current_app.logger.info(
                f"Seat allotment completed for round {allotment_round.round_number}. "
                f"Processed: {students_processed}, Allotted: {allotments_made}"
            )

            return {
                'round_number': allotment_round.round_number,
                'students_processed': students_processed,
                'allotments_made': allotments_made,
                'success': True
            }

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Seat allotment failed: {str(e)}")
            return {'error': str(e), 'success': False}

    @staticmethod
    def _check_category_seat(course, category):
        """Check if category-wise seat is available"""
        if category == 'General' and course.general_seats > 0:
            return True
        elif category == 'OBC' and course.obc_seats > 0:
            return True
        elif category == 'SC' and course.sc_seats > 0:
            return True
        elif category == 'ST' and course.st_seats > 0:
            return True
        elif category == 'EWS' and course.ews_seats > 0:
            return True
        return False

    @staticmethod
    def _reduce_category_seat(course, category):
        """Reduce category-wise seat count"""
        if category == 'General' and course.general_seats > 0:
            course.general_seats -= 1
        elif category == 'OBC' and course.obc_seats > 0:
            course.obc_seats -= 1
        elif category == 'SC' and course.sc_seats > 0:
            course.sc_seats -= 1
        elif category == 'ST' and course.st_seats > 0:
            course.st_seats -= 1
        elif category == 'EWS' and course.ews_seats > 0:
            course.ews_seats -= 1

    @staticmethod
    def accept_seat(allotment_id, freeze=True):
        """
        Accept an allotted seat

        Args:
            allotment_id: Allotment ID
            freeze: True to freeze (no upgrade), False to accept with upgrade option

        Returns:
            bool: True if successful
        """
        try:
            allotment = Allotment.query.get(allotment_id)
            if not allotment:
                return False

            if allotment.status != AllotmentStatus.ALLOTTED:
                current_app.logger.warning(f"Allotment {allotment_id} already processed")
                return False

            # Update status
            allotment.status = (
                AllotmentStatus.ACCEPTED_FROZEN if freeze
                else AllotmentStatus.ACCEPTED_UPGRADE
            )
            allotment.acceptance_date = datetime.utcnow()

            # If frozen, mark admission as confirmed
            if freeze:
                allotment.student.admission_confirmed = True
                current_app.logger.info(f"Student {allotment.student.id} admission confirmed")

            # Update round statistics
            allotment.round.accepted_count += 1

            db.session.commit()
            return True

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Seat acceptance failed: {str(e)}")
            return False

    @staticmethod
    def reject_seat(allotment_id, reason=None):
        """
        Reject an allotted seat

        Args:
            allotment_id: Allotment ID
            reason: Rejection reason

        Returns:
            bool: True if successful
        """
        try:
            allotment = Allotment.query.get(allotment_id)
            if not allotment:
                return False

            # Update status
            allotment.status = AllotmentStatus.REJECTED
            allotment.rejection_reason = reason
            allotment.acceptance_date = datetime.utcnow()

            # Restore seat availability
            course = allotment.course
            course.available_seats += 1

            # Restore category-wise seat
            if allotment.allotted_category == 'General':
                course.general_seats += 1
            elif allotment.allotted_category == 'OBC':
                course.obc_seats += 1
            elif allotment.allotted_category == 'SC':
                course.sc_seats += 1
            elif allotment.allotted_category == 'ST':
                course.st_seats += 1
            elif allotment.allotted_category == 'EWS':
                course.ews_seats += 1

            # Update round statistics
            allotment.round.rejected_count += 1

            db.session.commit()
            return True

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Seat rejection failed: {str(e)}")
            return False
