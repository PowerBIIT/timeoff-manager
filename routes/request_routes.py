"""Request (wniosek) management routes"""
from flask import Blueprint, request, jsonify, g
from models import db, Request, User
from auth import token_required, require_role
from services.audit_service import log_action
from services.email_service import send_new_request_email, send_decision_email
from datetime import datetime, date, time
from sqlalchemy import or_

request_bp = Blueprint('requests', __name__)


@request_bp.route('/requests', methods=['GET'])
@token_required
def get_requests():
    """
    Get requests based on user role
    GET /api/requests?status=oczekujący&employee_id=5
    Headers: { "Authorization": "Bearer <token>" }
    Returns: [{ "id": 1, "employee": {...}, "manager": {...}, ... }]
    """
    try:
        # Get query parameters
        status_filter = request.args.get('status')
        employee_id_filter = request.args.get('employee_id')
        manager_id_filter = request.args.get('manager_id')

        # Build query based on user role
        if g.user_role == 'pracownik':
            # Employee sees only their own requests
            query = Request.query.filter_by(employee_id=g.user_id)
        elif g.user_role == 'manager':
            # Manager sees their own requests + requests from their team
            query = Request.query.filter(
                or_(
                    Request.employee_id == g.user_id,
                    Request.manager_id == g.user_id
                )
            )
        else:  # admin
            # Admin sees all requests
            query = Request.query

        # Apply filters
        if status_filter:
            query = query.filter_by(status=status_filter)
        if employee_id_filter:
            query = query.filter_by(employee_id=int(employee_id_filter))
        if manager_id_filter:
            query = query.filter_by(manager_id=int(manager_id_filter))

        # Order by created_at desc
        requests = query.order_by(Request.created_at.desc()).all()

        return jsonify([req.to_dict() for req in requests]), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@request_bp.route('/requests', methods=['POST'])
@token_required
def create_request():
    """
    Create new request
    POST /api/requests
    Body: {
        "date": "2025-10-15",
        "time_out": "10:00",
        "time_return": "12:00",
        "reason": "Wizyta u lekarza"
    }
    Returns: { "success": true, "request_id": 1, "email_sent": true }
    Note: manager_id is automatically determined from user's supervisor_id
    """
    try:
        data = request.get_json()

        # Validation
        required_fields = ['date', 'time_out', 'time_return', 'reason']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Field {field} is required'}), 400

        # Validate reason length
        if len(data['reason']) < 10:
            return jsonify({'error': 'Reason must be at least 10 characters long'}), 400

        # Parse date and time
        request_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        time_out = datetime.strptime(data['time_out'], '%H:%M').time()
        time_return = datetime.strptime(data['time_return'], '%H:%M').time()

        # Validate date (cannot be in past)
        if request_date < date.today():
            return jsonify({'error': 'Date cannot be in the past'}), 400

        # Validate times
        if time_return <= time_out:
            return jsonify({'error': 'Return time must be after out time'}), 400

        # Get current user's supervisor (this becomes the manager for the request)
        current_user = User.query.get(g.user_id)
        if not current_user.supervisor_id:
            return jsonify({'error': 'You must have a supervisor assigned to create requests'}), 400

        supervisor = User.query.get(current_user.supervisor_id)
        if not supervisor:
            return jsonify({'error': 'Your supervisor not found in system'}), 404

        # Create request
        new_request = Request(
            employee_id=g.user_id,
            manager_id=current_user.supervisor_id,
            date=request_date,
            time_out=time_out,
            time_return=time_return,
            reason=data['reason'],
            status='oczekujący'
        )

        db.session.add(new_request)
        db.session.commit()

        # Get employee info
        employee = User.query.get(g.user_id)
        employee_name = f"{employee.first_name} {employee.last_name}"

        # Send email to supervisor (manager of the request)
        email_sent = False
        try:
            success, msg = send_new_request_email(
                supervisor.email,
                employee_name,
                {
                    'date': data['date'],
                    'time_out': data['time_out'],
                    'time_return': data['time_return'],
                    'reason': data['reason']
                }
            )
            email_sent = success
        except Exception as email_error:
            print(f"Email error: {str(email_error)}")

        # Log action
        log_action(
            g.user_id,
            'REQUEST_CREATED',
            f'Created request for {data["date"]} - {data["time_out"]} to {data["time_return"]}'
        )

        return jsonify({
            'success': True,
            'request_id': new_request.id,
            'email_sent': email_sent
        }), 201

    except ValueError as ve:
        return jsonify({'error': f'Invalid date/time format: {str(ve)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@request_bp.route('/requests/<int:request_id>/accept', methods=['PUT'])
@require_role('manager', 'admin')
def accept_request(request_id):
    """
    Accept request
    PUT /api/requests/:id/accept
    Headers: { "Authorization": "Bearer <token>" }
    Returns: { "success": true, "email_sent": true }
    """
    try:
        req = Request.query.get(request_id)

        if not req:
            return jsonify({'error': 'Request not found'}), 404

        # Check if manager can accept this request
        if g.user_role == 'manager' and req.manager_id != g.user_id:
            return jsonify({'error': 'You can only accept requests assigned to you'}), 403

        # Check status
        if req.status != 'oczekujący':
            return jsonify({'error': f'Cannot accept request with status: {req.status}'}), 400

        # Update request
        req.status = 'zaakceptowany'
        req.decision_date = datetime.utcnow()
        db.session.commit()

        # Get employee info
        employee = req.employee
        employee_name = f"{employee.first_name} {employee.last_name}"

        # Send email to employee
        email_sent = False
        try:
            success, msg = send_decision_email(
                employee.email,
                employee_name,
                {
                    'date': req.date.isoformat(),
                    'time_out': req.time_out.strftime('%H:%M'),
                    'time_return': req.time_return.strftime('%H:%M')
                },
                'zaakceptowany'
            )
            email_sent = success
        except Exception as email_error:
            print(f"Email error: {str(email_error)}")

        # Log action
        log_action(
            g.user_id,
            'REQUEST_ACCEPTED',
            f'Accepted request #{request_id} from {employee_name}'
        )

        return jsonify({
            'success': True,
            'email_sent': email_sent
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@request_bp.route('/requests/<int:request_id>/reject', methods=['PUT'])
@require_role('manager', 'admin')
def reject_request(request_id):
    """
    Reject request
    PUT /api/requests/:id/reject
    Body: { "comment": "Zbyt krótkie wyprzedzenie" }
    Headers: { "Authorization": "Bearer <token>" }
    Returns: { "success": true, "email_sent": true }
    """
    try:
        data = request.get_json()
        comment = data.get('comment', '')

        req = Request.query.get(request_id)

        if not req:
            return jsonify({'error': 'Request not found'}), 404

        # Check if manager can reject this request
        if g.user_role == 'manager' and req.manager_id != g.user_id:
            return jsonify({'error': 'You can only reject requests assigned to you'}), 403

        # Check status
        if req.status != 'oczekujący':
            return jsonify({'error': f'Cannot reject request with status: {req.status}'}), 400

        # Update request
        req.status = 'odrzucony'
        req.decision_date = datetime.utcnow()
        req.manager_comment = comment
        db.session.commit()

        # Get employee info
        employee = req.employee
        employee_name = f"{employee.first_name} {employee.last_name}"

        # Send email to employee
        email_sent = False
        try:
            success, msg = send_decision_email(
                employee.email,
                employee_name,
                {
                    'date': req.date.isoformat(),
                    'time_out': req.time_out.strftime('%H:%M'),
                    'time_return': req.time_return.strftime('%H:%M')
                },
                'odrzucony',
                comment
            )
            email_sent = success
        except Exception as email_error:
            print(f"Email error: {str(email_error)}")

        # Log action
        log_action(
            g.user_id,
            'REQUEST_REJECTED',
            f'Rejected request #{request_id} from {employee_name}. Comment: {comment}'
        )

        return jsonify({
            'success': True,
            'email_sent': email_sent
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@request_bp.route('/requests/<int:request_id>', methods=['DELETE'])
@token_required
def cancel_request(request_id):
    """
    Cancel (delete) request - only employee who created it can cancel
    DELETE /api/requests/:id
    Headers: { "Authorization": "Bearer <token>" }
    Returns: { "success": true }
    """
    try:
        req = Request.query.get(request_id)

        if not req:
            return jsonify({'error': 'Request not found'}), 404

        # Check if user is the employee who created the request
        if req.employee_id != g.user_id:
            return jsonify({'error': 'You can only cancel your own requests'}), 403

        # Check status - can only cancel pending requests
        if req.status != 'oczekujący':
            return jsonify({'error': 'Can only cancel pending requests'}), 400

        # Change status to anulowany instead of deleting
        req.status = 'anulowany'
        db.session.commit()

        # Log action
        log_action(
            g.user_id,
            'REQUEST_CANCELLED',
            f'Cancelled request #{request_id} for {req.date.isoformat()}'
        )

        return jsonify({'success': True}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
