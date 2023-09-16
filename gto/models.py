from json.decoder import JSONDecodeError
from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
import datetime
import json


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    email = db.Column(db.String(256), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    registration_timestamp = db.Column(
        db.DateTime, nullable=False, default=datetime.datetime.now())
    registration_date = db.Column(
        db.DateTime, nullable=False, default=datetime.date.today())
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmation_timestamp = db.Column(db.DateTime, nullable=True)
    is_pro = db.Column(db.Boolean, default=False)
    pro_validity = db.Column(db.DateTime)
    disabled = db.Column(db.Boolean, default=False)
    processing_balance = db.Column(db.Integer, default=0)
    device_id = db.Column(db.Text, nullable=True)

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.email = kwargs.get("email")
        self.password_hash = generate_password_hash(
            kwargs.get("password_hash"))
        self.registration_timestamp = datetime.datetime.now()
        self.registration_date = datetime.datetime.today()
        self.admin = False
        self.is_confirmed = False
        self.confirmation_timestamp = datetime.datetime(2001, 1, 1)
        self.pro_user = False
        self.pro_validity = datetime.datetime(2001, 1, 1)
        self.processing_balance = kwargs.get("processing_balance")
        self.disabled = False
        self.device_id = json.dumps([])

    def get_email(self):
        return self.email

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_remaining_hands(self):
        try:
            return self.processing_balance
        except UnboundLocalError:
            return 0

    def add_device_id(self, new_device_id):
        try:
            if new_device_id not in json.loads(self.device_id):
                self.device_id = json.dumps(json.loads(
                    self.device_id) + [new_device_id, ])
        except JSONDecodeError:
            self.device_id = json.dumps([new_device_id, ])
        except UnboundLocalError:
            self.device_id = json.dumps([new_device_id, ])

    def get_device_ids(self):
        try:
            json.dumps(json.loads(self.device_id))
        except JSONDecodeError:
            return []
        except UnboundLocalError:
            return []


class LoginHistory(db.Model):
    __tablename__ = "login_history"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256))
    login_timestamp = db.Column(db.DateTime)
    session_key = db.Column(db.String(256))
    ip_address = db.Column(db.String(256))
    user_agent = db.Column(db.String(128))
    browser_fingerprint = db.Column(db.String(256))

    def __init__(self, **kwargs):
        self.email = kwargs.get("email")
        self.login_timestamp = datetime.datetime.now()
        self.session_key = kwargs.get("session_key")
        self.user_agent = kwargs.get("user_agent")
        self.ip_address = kwargs.get("ip_address")


class Logins(db.Model):
    __tablename__ = "last_login_info"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256))
    login_timestamp = db.Column(db.DateTime)
    session_key = db.Column(db.String(256))
    ip_address = db.Column(db.String(256))
    user_agent = db.Column(db.String(128))
    browser_fingerprint = db.Column(db.String(256))

    def __init__(self, **kwargs):
        self.email = kwargs.get("email")
        self.login_timestamp = datetime.datetime.now()
        self.session_key = kwargs.get("session_key")
        self.user_agent = kwargs.get("user_agent")
        self.ip_address = kwargs.get("ip_address")

    def get_session_key(self):
        return str(self.session_key)


class PaymentHistory(db.Model):
    __tablename__ = "purchase_history"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(128))
    payment_id = db.Column(db.String(256))
    payment_email = db.Column(db.String(128))
    payment_phone_number = db.Column(db.String(64))
    amount = db.Column(db.Numeric)
    payment_time = db.Column(db.DateTime, default=datetime.datetime.now())
    payment_currency = db.Column(db.String(64))
    coupon_used = db.Column(db.String(64), default=None)
    hands = db.Column(db.Integer)

    def __init__(self, **kwargs):
        self.user_id = current_user.get_id()
        self.payment_id = kwargs.get("payment_id")
        self.payment_email = kwargs.get('email')
        self.payment_phone_number = kwargs.get("phone")
        self.payment_time = kwargs.get("payment_time", datetime.datetime.now())
        self.amount = kwargs.get("amount")
        self.payment_currency = kwargs.get("currency", "INR")
        self.coupon_used = kwargs.get("coupon_code", "")
        self.hands = kwargs.get("hands")


class HandHistoryDatabase(db.Model):

    __tablename__ = "hand_history_upload"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128))
    original_filename = db.Column(db.String(512))
    morphed_filename = db.Column(db.String(256))
    file_format = db.Column(db.String(64))
    upload_timestamp = db.Column(db.DateTime, default=datetime.datetime.now())
    processing_time = db.Column(db.Integer, default=0)
    number_of_hands = db.Column(db.Integer, default=0)
    number_of_hands_processed = db.Column(db.Integer, default=0)
    is_processed = db.Column(db.Boolean, default=False)

    def __init__(self, **kwargs):
        self.email = kwargs.get("email", current_user.get_email())
        self.original_filename = kwargs.get("original_filename")
        self.morphed_filename = kwargs.get("morphed_filename")
        self.file_format = kwargs.get("file_format")
        self.upload_timestamp = kwargs.get(
            "upload_timestamp", datetime.datetime.now())
        self.processing_time = kwargs.get("processing_time", 0)
        self.number_of_hands = kwargs.get("number_of_hands", 0)
        self.number_of_hands_processed = kwargs.get(
            "number_of_hands_processed", 0)
        self.is_processed = kwargs.get("is_processed", False)


class CouponsUseHistory(db.Model):
    __tablename__ = "coupon_use_history"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), nullable=False)
    coupon_code = db.Column(db.String(128), nullable=False)
    coupon_type = db.Column(db.String(64), nullable=False)
    coupon_discount_percentage = db.Column(db.Integer)
    coupon_hands_given = db.Column(db.Integer)

    def __init__(self, **kwargs):
        self.email = kwargs.get('email', current_user.get_email())
        self.coupon_code = kwargs.get('coupon_code')
        self.coupon_type = kwargs.get('coupon_type')
        self.coupon_discount_percentage = kwargs.get(
            'coupon_discount_percentage')
        self.coupon_hands_given = kwargs.get('coupon_hands_given')


class Coupon(db.Model):

    __tablename__ = 'coupon'
    id = db.Column(db.Integer, primary_key=True)
    coupon_code = db.Column(db.String(64), unique=True)
    coupon_type = db.Column(db.String(64))
    coupon_discount_percentage = db.Column(db.Integer)
    coupon_hands = db.Column(db.Integer)

    def __init__(self, **kwargs) -> None:
        self.coupon_code = kwargs.get("coupon_code")
        self.coupon_type = kwargs.get("coupon_type")
        self.coupon_discount_percentage = kwargs.get(
            "coupon_discount_percentage", 0)
        self.coupon_hands = kwargs.get("coupon_hands", 0)

    def get_coupon_data(self):
        return self.coupon_type, self.coupon_discount_percentage, self.coupon_hands


# class Heronames(db.Model):
#     __tablename__ = 'heronames'


# class HeroNames(db.Model):
#     __tablename__ = "heronames"
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(256))
#     hero = db.Column(db.String(256))
