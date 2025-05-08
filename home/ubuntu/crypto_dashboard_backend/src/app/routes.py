from flask import Blueprint, jsonify, request
# Placeholder for services that will handle the business logic
from .services import alert_service # Assuming other services like crypto_service and report_service will be added

main_bp = Blueprint("main_bp", __name__, url_prefix="/api")

@main_bp.route("/")
def index():
    return jsonify({"message": "Welcome to the Crypto Analysis API!"})

# --- Crypto Data Endpoints (Placeholders) ---
@main_bp.route("/crypto/prices", methods=["GET"])
def get_crypto_prices():
    symbol = request.args.get("symbol", default="BTC-USD", type=str)
    range_param = request.args.get("range", default="7d", type=str)
    # data = crypto_service.get_price_history(symbol, range_param)
    return jsonify({
        "message": f"Endpoint to get price history for {symbol} over {range_param}",
        "symbol": symbol,
        "range": range_param,
        "data": [] 
    })

@main_bp.route("/crypto/analysis", methods=["GET"])
def get_crypto_analysis():
    symbol = request.args.get("symbol", default="BTC-USD", type=str)
    # analysis = crypto_service.get_current_analysis(symbol)
    return jsonify({
        "message": f"Endpoint to get current analysis for {symbol}",
        "symbol": symbol,
        "analysis": {}
    })

@main_bp.route("/crypto/prediction", methods=["GET"])
def get_crypto_prediction():
    symbol = request.args.get("symbol", default="BTC-USD", type=str)
    # prediction = crypto_service.get_prediction(symbol)
    return jsonify({
        "message": f"Endpoint to get prediction for {symbol}",
        "symbol": symbol,
        "prediction": {}
    })

# --- Reports Endpoints (Placeholders) ---
@main_bp.route("/reports/latest", methods=["GET"])
def get_latest_report():
    format_param = request.args.get("format", default="pdf", type=str.lower)
    # report_data = report_service.get_latest_report(format_param)
    if format_param not in ["pdf", "md"]:
        return jsonify({"error": "Invalid format. Choose pdf or md."}), 400
    return jsonify({
        "message": f"Endpoint to get the latest report in {format_param} format",
        "format": format_param,
        "report_content": "Placeholder for report content or link"
    })

@main_bp.route("/reports/archive", methods=["GET"])
def get_reports_archive():
    # archive_list = report_service.get_archive_list()
    return jsonify({
        "message": "Endpoint to get the list of archived reports",
        "archive": []
    })

@main_bp.route("/reports/download/<report_id>", methods=["GET"])
def download_report(report_id):
    format_param = request.args.get("format", default="pdf", type=str.lower)
    # file_path = report_service.get_report_file(report_id, format_param)
    # if file_path: return send_file(file_path, as_attachment=True)
    if format_param not in ["pdf", "md"]:
        return jsonify({"error": "Invalid format. Choose pdf or md."}), 400
    return jsonify({
        "message": f"Endpoint to download report {report_id} in {format_param} format",
        "report_id": report_id,
        "format": format_param,
        "download_link": f"/path/to/report_{report_id}.{format_param}"
    })

# --- User Settings (Placeholder) ---
@main_bp.route("/user/settings", methods=["GET", "POST"])
def user_settings():
    user_identifier = request.args.get("userId") # Or get from auth header
    if not user_identifier:
        return jsonify({"error": "User identifier is required"}), 400

    if request.method == "GET":
        # settings = user_service.get_settings(user_identifier)
        return jsonify({"message": f"GET user settings for {user_identifier}", "settings": {"mock_setting": True}})
    elif request.method == "POST":
        settings_data = request.json
        # result = user_service.update_settings(user_identifier, settings_data)
        return jsonify({"message": f"POST (update) user settings for {user_identifier}", "received_data": settings_data})

# --- Alert System Endpoints ---
@main_bp.route("/alerts/subscriptions", methods=["GET"])
def get_alert_subscriptions():
    user_identifier = request.args.get("userId") # Or from auth
    if not user_identifier:
        return jsonify({"error": "User identifier is required for fetching subscriptions"}), 400
    subscriptions = alert_service.get_user_alert_subscriptions(user_identifier)
    return jsonify({"status": "success", "subscriptions": subscriptions})

@main_bp.route("/alerts/subscribe", methods=["POST"])
def subscribe_alerts():
    data = request.json
    user_identifier = data.get("userId")
    crypto_symbol = data.get("cryptoSymbol")
    alert_condition = data.get("alertCondition")
    if not all([user_identifier, crypto_symbol, alert_condition]):
        return jsonify({"error": "Missing data for alert subscription (userId, cryptoSymbol, alertCondition required)"}), 400
    
    result = alert_service.subscribe_to_alerts(user_identifier, crypto_symbol, alert_condition)
    return jsonify(result)

@main_bp.route("/alerts/unsubscribe", methods=["POST"])
def unsubscribe_alerts():
    data = request.json
    user_identifier = data.get("userId")
    crypto_symbol = data.get("cryptoSymbol")
    alert_condition = data.get("alertCondition") # Or perhaps a subscription ID
    if not all([user_identifier, crypto_symbol, alert_condition]):
        return jsonify({"error": "Missing data for alert unsubscription (userId, cryptoSymbol, alertCondition required)"}), 400

    result = alert_service.unsubscribe_from_alerts(user_identifier, crypto_symbol, alert_condition)
    return jsonify(result)

