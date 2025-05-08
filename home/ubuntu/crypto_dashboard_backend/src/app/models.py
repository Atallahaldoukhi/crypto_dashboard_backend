from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize SQLAlchemy. This will be configured in create_app in __init__.py
db = SQLAlchemy()

class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    report_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    crypto_symbol = db.Column(db.String(20), nullable=False) # e.g., BTC-USD, ETH-USD
    # Storing summaries might be redundant if they are in the report files, but can be useful for quick display
    analysis_summary = db.Column(db.Text, nullable=True)
    prediction_summary = db.Column(db.Text, nullable=True)
    md_file_path = db.Column(db.String(255), nullable=True) # Path to the markdown file
    pdf_file_path = db.Column(db.String(255), nullable=True) # Path to the PDF file
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Report {self.crypto_symbol} on {self.report_date}>"

class UserPreference(db.Model):
    __tablename__ = "user_preferences"
    # This is a placeholder model. Full implementation requires user authentication.
    id = db.Column(db.Integer, primary_key=True)
    user_identifier = db.Column(db.String(100), unique=True, nullable=False) # Could be email or a unique ID
    followed_cryptos = db.Column(db.Text, nullable=True) # e.g., comma-separated list: "BTC-USD,ETH-USD"
    alert_settings_json = db.Column(db.Text, nullable=True) # Store complex settings as JSON string
    report_preferences_json = db.Column(db.Text, nullable=True) # Store complex settings as JSON string
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<UserPreference {self.user_identifier}>"

class AlertSubscription(db.Model):
    __tablename__ = "alert_subscriptions"
    # This is a placeholder model. Full implementation requires a robust alert system.
    id = db.Column(db.Integer, primary_key=True)
    user_identifier = db.Column(db.String(100), db.ForeignKey("user_preferences.user_identifier"), nullable=False)
    crypto_symbol = db.Column(db.String(20), nullable=False)
    alert_condition = db.Column(db.String(255), nullable=False) # e.g., "price_increase_5_percent"
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_alert_sent_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("UserPreference", backref=db.backref("alerts", lazy=True))

    def __repr__(self):
        return f"<AlertSubscription {self.user_identifier} for {self.crypto_symbol}>"

# You would typically add functions here to interact with these models,
# or handle that logic in service layers.

