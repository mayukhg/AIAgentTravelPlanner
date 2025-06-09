import asyncio
import logging
from flask import Blueprint, request, jsonify, session
from graph.workflow import MultiAgentWorkflow
import uuid

api_bp = Blueprint('api', __name__)

# Initialize the workflow (this will be shared across requests)
workflow = None

def get_workflow():
    """Get or initialize the workflow instance"""
    global workflow
    if workflow is None:
        workflow = MultiAgentWorkflow()
    return workflow

@api_bp.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": "Message is required"
            }), 400
        
        user_message = data['message'].strip()
        if not user_message:
            return jsonify({
                "success": False,
                "error": "Message cannot be empty"
            }), 400
        
        # Get or create session ID
        session_id = data.get('session_id') or session.get('session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id
        
        # Process the message through the workflow
        workflow_instance = get_workflow()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                workflow_instance.process_user_input(user_message, session_id)
            )
        finally:
            loop.close()
        
        if result.get('success'):
            agent_result = result.get('result', {})
            
            response = {
                "success": True,
                "message": agent_result.get('content', ''),
                "agent_type": agent_result.get('agent_type', 'unknown'),
                "session_id": session_id,
                "metadata": {
                    "timestamp": agent_result.get('timestamp'),
                    "delegated_to": agent_result.get('delegated_to'),
                    "action_performed": agent_result.get('action_performed')
                }
            }
            
            # Add additional data if available
            if 'citations' in agent_result:
                response['citations'] = agent_result['citations']
            if 'event_data' in agent_result:
                response['event_data'] = agent_result['event_data']
                
            return jsonify(response)
        else:
            return jsonify({
                "success": False,
                "error": result.get('error', 'Unknown error occurred'),
                "session_id": session_id
            }), 500
            
    except Exception as e:
        logging.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500

@api_bp.route('/workflow/status/<session_id>', methods=['GET'])
def workflow_status(session_id):
    """Get workflow status"""
    try:
        workflow_instance = get_workflow()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            status = loop.run_until_complete(
                workflow_instance.get_workflow_status(session_id)
            )
        finally:
            loop.close()
        
        return jsonify(status)
        
    except Exception as e:
        logging.error(f"Error getting workflow status: {str(e)}")
        return jsonify({
            "error": str(e)
        }), 500

@api_bp.route('/agents', methods=['GET'])
def get_agents():
    """Get available agents information"""
    try:
        workflow_instance = get_workflow()
        agents = workflow_instance.get_available_agents()
        
        return jsonify({
            "success": True,
            "agents": agents
        })
        
    except Exception as e:
        logging.error(f"Error getting agents: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Comprehensive health check"""
    try:
        workflow_instance = get_workflow()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            health = loop.run_until_complete(
                workflow_instance.health_check()
            )
        finally:
            loop.close()
        
        return jsonify(health)
        
    except Exception as e:
        logging.error(f"Error in health check: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

@api_bp.route('/clear/<session_id>', methods=['DELETE'])
def clear_session(session_id):
    """Clear a specific session"""
    try:
        workflow_instance = get_workflow()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            success = loop.run_until_complete(
                workflow_instance.clear_workflow(session_id)
            )
        finally:
            loop.close()
        
        return jsonify({
            "success": success,
            "message": "Session cleared" if success else "Session not found"
        })
        
    except Exception as e:
        logging.error(f"Error clearing session: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
