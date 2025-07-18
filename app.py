import copy
import json
import logging
import os
import time
import uuid
from types import SimpleNamespace

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.monitor.opentelemetry import configure_azure_monitor
from flask import Flask
from quart import (
    Blueprint,
    Quart,
    Response,
    jsonify,
    render_template,
    request,
    send_from_directory,
)
from backend.services import chatbot_service
from backend.common.config import config
from backend.services import sqldnb_service
from backend.plugins.chat_with_data import ChatWithDataPlugin


bp = Blueprint("routes", __name__, static_folder="static", template_folder="static")

def create_app():

    app = Quart(__name__)
    app.register_blueprint(bp)
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    @app.before_serving
    async def startup():
        logging.info(
            "Call Transcript Search Agent initialized during application startup"
        )
    return app

@bp.route("/get_invoice_name/<invoice_id>", methods=["GET"])
async def get_invoice_name(invoice_id):
    try:
        invoice_name = sqldnb_service.get_invoice_name_from_db(invoice_id)
        return jsonify({"invoice_name": invoice_name})
    except Exception as e:
        logging.error(f"Error in get_invoice_name endpoint: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@bp.route("/get_invoice_history/<invoice_id>", methods=["GET"])
async def get_invoice_history(invoice_id):
    try:
        invoice_history = sqldnb_service.get_invoice_update_history_from_db(invoice_id)
        return jsonify({"invoice_history": invoice_history})
    except Exception as e:
        logging.error(f"Error in get_invoice_name endpoint: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
    
@bp.route("/chat_with_data", methods=["POST"])
async def chat_with_data():
    data = await request.json
    query = data.get("query")
    invoice_id = data.get("invoice_id")
    chat_with_data_plugin = ChatWithDataPlugin()
    response = await chat_with_data_plugin.get_SQL_Response(input=query, invoice_id=invoice_id)
    return jsonify({"response": str(response)})

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=50505, log_level="debug")