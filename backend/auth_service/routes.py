# From blueprint:python_log_in_with_replit integration
from flask import session, render_template, request, jsonify, url_for
from app import app, db
from replit_auth import require_login, make_replit_blueprint
from flask_login import current_user
from models import User, ConnectorCredential, UserToken
import hashlib
import secrets
import json
from datetime import datetime

app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")

# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route('/')
def index():
    """Landing page - shows login for anonymous users, dashboard for authenticated users"""
    if current_user.is_authenticated:
        return render_template('dashboard.html', user=current_user)
    else:
        return render_template('landing.html')

@app.route('/dashboard')
@require_login
def dashboard():
    """User dashboard with connected services"""
    user = current_user
    
    # Get user's connected services
    connected_services = []
    for cred in user.connector_credentials:
        connected_services.append({
            'name': cred.connector_name,
            'connected_at': cred.created_at
        })
    
    # Get user's API tokens  
    api_tokens = []
    for token in user.api_tokens:
        api_tokens.append({
            'id': token.id,
            'name': token.name,
            'created_at': token.created_at,
            'last_used': token.last_used
        })
    
    return render_template('dashboard.html', 
                         user=user, 
                         connected_services=connected_services,
                         api_tokens=api_tokens)

@app.route('/api/tokens', methods=['POST'])
@require_login
def create_api_token():
    """Create a new API token for the user"""
    data = request.get_json()
    token_name = data.get('name', 'API Token')
    
    # Generate a secure token
    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    
    # Store in database
    user_token = UserToken(
        user_id=current_user.id,
        token_hash=token_hash,
        name=token_name
    )
    db.session.add(user_token)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'token': raw_token,  # Only returned once!
        'token_id': user_token.id,
        'name': token_name
    })

@app.route('/api/tokens/<int:token_id>', methods=['DELETE'])
@require_login  
def delete_api_token(token_id):
    """Delete an API token"""
    token = UserToken.query.filter_by(
        id=token_id,
        user_id=current_user.id
    ).first()
    
    if not token:
        return jsonify({'error': 'Token not found'}), 404
    
    db.session.delete(token)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/user')
@require_login
def get_user_info():
    """Get current user information"""
    return jsonify({
        'id': current_user.id,
        'email': current_user.email,
        'first_name': current_user.first_name,
        'last_name': current_user.last_name,
        'profile_image_url': current_user.profile_image_url
    })

@app.route('/api/validate-token', methods=['POST'])
def validate_api_token():
    """Validate an API token for FastAPI"""
    data = request.get_json()
    token = data.get('token')
    
    if not token:
        return jsonify({'valid': False, 'error': 'No token provided'}), 400
    
    # Hash the provided token
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    # Look up the token
    user_token = UserToken.query.filter_by(token_hash=token_hash).first()
    
    if not user_token:
        return jsonify({'valid': False, 'error': 'Invalid token'}), 401
    
    # Update last used timestamp
    user_token.last_used = datetime.now()
    db.session.commit()
    
    return jsonify({
        'valid': True,
        'user_id': user_token.user_id,
        'user': {
            'id': user_token.user.id,
            'email': user_token.user.email,
            'first_name': user_token.user.first_name,
            'last_name': user_token.user.last_name
        }
    })

# Connector management endpoints
@app.route('/connect/<connector_name>')
@require_login
def connect_service(connector_name):
    """Start OAuth flow for connecting a service"""
    # TODO: Implement OAuth flows for each connector
    available_connectors = ['google_tasks', 'google_calendar', 'slack']
    
    if connector_name not in available_connectors:
        return "Unknown connector", 404
    
    return render_template('connect_service.html', 
                         connector_name=connector_name,
                         user=current_user)

@app.route('/api/connections')
@require_login
def list_connections():
    """List user's connected services"""
    connections = []
    for cred in current_user.connector_credentials:
        connections.append({
            'connector_name': cred.connector_name,
            'connected_at': cred.created_at.isoformat(),
            'updated_at': cred.updated_at.isoformat()
        })
    
    return jsonify({'connections': connections})

@app.route('/api/connections/<connector_name>', methods=['DELETE'])
@require_login
def disconnect_service(connector_name):
    """Disconnect a service"""
    cred = ConnectorCredential.query.filter_by(
        user_id=current_user.id,
        connector_name=connector_name
    ).first()
    
    if not cred:
        return jsonify({'error': 'Service not connected'}), 404
    
    db.session.delete(cred)
    db.session.commit()
    
    return jsonify({'success': True})

# Error handlers
@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404