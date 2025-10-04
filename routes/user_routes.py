"""User management routes (Admin only)"""
from flask import Blueprint, request, jsonify, g
from models import db, User, Request
from auth import require_role, hash_password
from services.audit_service import log_action

user_bp = Blueprint('users', __name__)


@user_bp.route('/users', methods=['GET'])
@require_role('admin', 'manager', 'pracownik')
def get_users():
    """
    Get all users (admin) or managers (all roles)
    GET /api/users?role=manager - accessible to all authenticated users
    GET /api/users - admin/manager only
    Headers: { "Authorization": "Bearer <token>" }
    Returns: [{ "id": 1, "email": "...", ... }]
    """
    try:
        role_filter = request.args.get('role')

        # Build query
        query = User.query

        # If role=manager filter requested, allow all authenticated users
        # (needed for employee to select manager in request form)
        if role_filter == 'manager':
            query = query.filter_by(role='manager')
        else:
            # Full user list - only admin and manager can access
            if g.user_role not in ['admin', 'manager']:
                return jsonify({'error': 'Access denied'}), 403

            # Filter by role if provided
            if role_filter:
                query = query.filter_by(role=role_filter)

            # If manager is requesting, only show managers and admins
            if g.user_role == 'manager':
                query = query.filter(User.role.in_(['manager', 'admin']))

        users = query.order_by(User.created_at.desc()).all()

        return jsonify([user.to_dict() for user in users]), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/users', methods=['POST'])
@require_role('admin')
def create_user():
    """
    Create new user (admin only)
    POST /api/users
    Body: {
        "email": "new@firma.pl",
        "password": "password123",
        "first_name": "Jan",
        "last_name": "Kowalski",
        "role": "pracownik",
        "supervisor_id": 2
    }
    Returns: { "success": true, "user_id": 10 }
    """
    try:
        data = request.get_json()

        # Validation
        required_fields = ['email', 'password', 'first_name', 'last_name', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Field {field} is required'}), 400

        # Validate role
        if data['role'] not in ['pracownik', 'manager', 'admin']:
            return jsonify({'error': 'Invalid role'}), 400

        # Validate password length
        if len(data['password']) < 8:
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400

        # Check if email already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'Email already exists'}), 409

        # If supervisor_id provided, validate it exists
        supervisor_id = data.get('supervisor_id')
        if supervisor_id:
            supervisor = User.query.get(supervisor_id)
            if not supervisor:
                return jsonify({'error': 'Supervisor not found'}), 404

        # Create user
        new_user = User(
            email=data['email'],
            password_hash=hash_password(data['password']),
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=data['role'],
            supervisor_id=supervisor_id
        )

        db.session.add(new_user)
        db.session.commit()

        # Log action
        log_action(
            g.user_id,
            'USER_CREATED',
            f'Created user {data["email"]} with role {data["role"]}'
        )

        return jsonify({
            'success': True,
            'user_id': new_user.id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@require_role('admin')
def update_user(user_id):
    """
    Update user (admin only)
    PUT /api/users/:id
    Body: {
        "first_name": "Jan",
        "last_name": "Nowak",
        "role": "manager",
        "supervisor_id": 3,
        "is_active": true
    }
    Returns: { "success": true }
    """
    try:
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()

        # Update fields if provided
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'role' in data:
            if data['role'] not in ['pracownik', 'manager', 'admin']:
                return jsonify({'error': 'Invalid role'}), 400
            user.role = data['role']
        if 'supervisor_id' in data:
            # Validate supervisor exists
            if data['supervisor_id']:
                supervisor = User.query.get(data['supervisor_id'])
                if not supervisor:
                    return jsonify({'error': 'Supervisor not found'}), 404
            user.supervisor_id = data['supervisor_id']
        if 'is_active' in data:
            user.is_active = data['is_active']

        # Update password if provided
        if 'password' in data and data['password']:
            if len(data['password']) < 8:
                return jsonify({'error': 'Password must be at least 8 characters long'}), 400
            user.password_hash = hash_password(data['password'])

        db.session.commit()

        # Log action
        log_action(
            g.user_id,
            'USER_UPDATED',
            f'Updated user {user.email}'
        )

        return jsonify({'success': True}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@user_bp.route('/users/<int:user_id>/subordinates', methods=['GET'])
@require_role('admin')
def get_user_subordinates(user_id):
    """
    Get list of users supervised by this user
    GET /api/users/:id/subordinates
    Headers: { "Authorization": "Bearer <token>" }
    Returns: [{ "id": 1, "first_name": "Jan", "last_name": "Nowak", ... }]
    """
    try:
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Find all users who have this user as supervisor
        subordinates = User.query.filter_by(supervisor_id=user_id).all()

        return jsonify({
            'count': len(subordinates),
            'subordinates': [s.to_dict() for s in subordinates]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/users/<int:user_id>/reassign-subordinates', methods=['POST'])
@require_role('admin')
def reassign_subordinates(user_id):
    """
    Reassign all subordinates to a new supervisor
    POST /api/users/:id/reassign-subordinates
    Body: { "new_supervisor_id": 5 }
    Headers: { "Authorization": "Bearer <token>" }
    Returns: { "success": true, "reassigned_count": 3 }
    """
    try:
        data = request.get_json()
        new_supervisor_id = data.get('new_supervisor_id')

        # Validate new supervisor exists and is active
        if new_supervisor_id:
            new_supervisor = User.query.get(new_supervisor_id)
            if not new_supervisor:
                return jsonify({'error': 'New supervisor not found'}), 404
            if not new_supervisor.is_active:
                return jsonify({'error': 'New supervisor is not active'}), 400

        # Find all subordinates
        subordinates = User.query.filter_by(supervisor_id=user_id).all()

        # Reassign them
        for subordinate in subordinates:
            subordinate.supervisor_id = new_supervisor_id

        db.session.commit()

        # Log action
        log_action(
            g.user_id,
            'SUBORDINATES_REASSIGNED',
            f'Reassigned {len(subordinates)} subordinates from user {user_id} to {new_supervisor_id}'
        )

        return jsonify({
            'success': True,
            'reassigned_count': len(subordinates)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@require_role('admin')
def delete_user(user_id):
    """
    Delete user (admin only)
    DELETE /api/users/:id
    Headers: { "Authorization": "Bearer <token>" }
    Returns: { "success": true }
    """
    try:
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Cannot delete yourself
        if user.id == g.user_id:
            return jsonify({'error': 'Cannot delete your own account'}), 400

        # Check if user has requests (as employee)
        requests_count = Request.query.filter_by(employee_id=user_id).count()
        if requests_count > 0:
            return jsonify({
                'error': f'Cannot delete user with {requests_count} requests. Consider deactivating instead.'
            }), 400

        email = user.email
        db.session.delete(user)
        db.session.commit()

        # Log action
        log_action(
            g.user_id,
            'USER_DELETED',
            f'Deleted user {email}'
        )

        return jsonify({'success': True}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@user_bp.route('/users/<int:user_id>', methods=['GET'])
@require_role('admin', 'manager')
def get_user(user_id):
    """
    Get single user details
    GET /api/users/:id
    Headers: { "Authorization": "Bearer <token>" }
    Returns: { "id": 1, "email": "...", ... }
    """
    try:
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify(user.to_dict()), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
