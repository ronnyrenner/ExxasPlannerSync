from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required
from datetime import datetime
import logging
from app import db, scheduler
from models import Config, SyncLog

sync_bp = Blueprint('sync', __name__)
logger = logging.getLogger(__name__)

@sync_bp.route('/')
@login_required
def dashboard():
    config = Config.query.first()
    recent_logs = SyncLog.query.order_by(SyncLog.timestamp.desc()).limit(10).all()
    return render_template('dashboard.html', config=config, logs=recent_logs)

@sync_bp.route('/config', methods=['GET', 'POST'])
@login_required
def config():
    if request.method == 'POST':
        try:
            config = Config.query.first() or Config()
            config.exxas_api_url = request.form['exxas_api_url']
            config.exxas_api_key = request.form['exxas_api_key']
            config.ms_tenant_id = request.form['ms_tenant_id']
            config.ms_client_id = request.form['ms_client_id']
            config.ms_client_secret = request.form['ms_client_secret']
            config.sync_interval = int(request.form['sync_interval'])
            config.last_updated = datetime.utcnow()
            
            db.session.add(config)
            db.session.commit()
            flash('Configuration updated successfully', 'success')
            
            # Update scheduler
            scheduler.remove_all_jobs()
            scheduler.add_job(
                sync_data,
                'interval',
                minutes=config.sync_interval,
                id='sync_job'
            )
        except Exception as e:
            flash(f'Error updating configuration: {str(e)}', 'error')
            logger.error(f'Configuration update error: {str(e)}')
            
    config = Config.query.first()
    return render_template('config.html', config=config)

@sync_bp.route('/logs')
@login_required
def logs():
    page = request.args.get('page', 1, type=int)
    logs = SyncLog.query.order_by(SyncLog.timestamp.desc()).paginate(
        page=page, per_page=20, error_out=False)
    return render_template('logs.html', logs=logs)

@sync_bp.route('/trigger-sync', methods=['POST'])
@login_required
def trigger_sync():
    try:
        sync_data()
        return jsonify({'status': 'success', 'message': 'Sync triggered successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

def sync_data():
    """
    Performs the actual data synchronization between Exxas ERP and MS Planner
    """
    try:
        config = Config.query.first()
        if not config:
            raise Exception("Configuration not found")
            
        # Log sync start
        log = SyncLog(status="STARTED", message="Starting sync process")
        db.session.add(log)
        db.session.commit()
        
        # TODO: Implement actual sync logic here
        # This is where you would add the API calls to both systems
        
        # Log successful completion
        log.status = "COMPLETED"
        log.message = "Sync completed successfully"
        db.session.commit()
        
    except Exception as e:
        logger.error(f"Sync error: {str(e)}")
        log = SyncLog(status="ERROR", message=str(e))
        db.session.add(log)
        db.session.commit()
        raise
