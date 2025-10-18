"""
Flask API for Remote Builder Webhooks
POC Implementation per ROADMAP.md requirements

Provides Flask webhook endpoints for remote build triggering
Integrates with existing RemoteBuilder core class
"""



from flask import Flask, request, jsonify
import logging
from datetime import datetime
from typing import Dict, Any

from .remote_builder import RemoteBuilder, create_build_request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure Flask app for remote builder webhooks"""
    
    app = Flask(__name__)
    app.config['JSON_SORT_KEYS'] = False
    
    # Initialize RemoteBuilder instance
    builder = RemoteBuilder()
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint for monitoring"""
        
        return jsonify({
            "status": "healthy",
            "service": "remote_builder_flask_api",
            "timestamp": datetime.now().isoformat(),
            "version": "0.1.0-poc"
        })
    
    @app.route('/webhook/build', methods=['POST'])
    def webhook_build():
        """
        Main webhook endpoint for remote build triggering
        POC implementation per ROADMAP.md
        """
        
        try:
            # Parse JSON request
            data = request.get_json()
            
            if not data:
                return jsonify({
                    "error": "Missing JSON payload"
                }), 400
            
            # Extract required fields
            action = data.get('action', 'create_module')
            target = data.get('target') or data.get('module_name')
            
            if not target:
                return jsonify({
                    "error": "Missing 'target' or 'module_name' field"
                }), 400
            
            # Create build request using existing helper
            build_request = create_build_request(
                action=action,
                target=target,
                domain=data.get('domain', 'development'),
                parameters=data.get('parameters'),
                requester='webhook_client'
            )
            
            # Execute build using existing RemoteBuilder
            result = builder.execute_build(build_request)
            
            # Return response per ROADMAP requirements
            response_data = {
                "build_id": result.build_id,
                "success": result.success,
                "message": result.message,
                "action": result.action,
                "target": result.target,
                "timestamp": result.timestamp
            }
            
            # Include details if available
            if result.details:
                response_data["details"] = result.details
            
            status_code = 200 if result.success else 500
            
            logger.info(f"Webhook build triggered: {result.build_id} - {result.action} -> {result.target}")
            
            return jsonify(response_data), status_code
            
        except Exception as e:
            logger.error(f"Webhook build failed: {e}")
            
            return jsonify({
                "error": "Build execution failed",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    @app.route('/api/build/status', methods=['GET'])
    def build_status():
        """Get build status by ID - POC implementation"""
        
        build_id = request.args.get('build_id')
        
        if not build_id:
            return jsonify({
                "error": "Missing 'build_id' parameter"
            }), 400
        
        # Get build result from builder
        result = builder.get_build_by_id(build_id)
        
        if not result:
            return jsonify({
                "error": f"Build not found: {build_id}"
            }), 404
        
        return jsonify({
            "build_id": result.build_id,
            "success": result.success,
            "action": result.action,
            "target": result.target,
            "message": result.message,
            "timestamp": result.timestamp,
            "details": result.details
        })
    
    @app.route('/api/build/history', methods=['GET'])
    def build_history():
        """Get recent build history - POC implementation"""
        
        history = builder.get_build_history()
        
        # Return last 10 builds
        recent_builds = []
        for build in history[-10:]:
            recent_builds.append({
                "build_id": build.build_id,
                "success": build.success,
                "action": build.action,
                "target": build.target,
                "message": build.message,
                "timestamp": build.timestamp
            })
        
        return jsonify({
            "builds": recent_builds,
            "total_builds": len(history),
            "showing": len(recent_builds)
        })
    
    return app

def start_flask_server(host='localhost', port=5000, debug=False):
    """
    Start Flask server for webhook endpoints
    POC helper function per ROADMAP.md
    """
    
    app = create_app()
    
    logger.info(f"🚀 Starting Remote Builder Flask API on http://{host}:{port}")
    logger.info("📋 Available endpoints:")
    logger.info("  POST /webhook/build - Main webhook for build triggering")
    logger.info("  GET  /health - Health check")
    logger.info("  GET  /api/build/status?build_id=X - Build status")
    logger.info("  GET  /api/build/history - Recent build history")
    
    app.run(host=host, port=port, debug=debug)

# For direct execution testing
if __name__ == '__main__':
    start_flask_server(debug=True) 