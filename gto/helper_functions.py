import random
from itsdangerous import URLSafeTimedSerializer
from . import __base__ as base
import razorpay
import os
import hashlib
import time
import boto3


class HelperFunctions(object):

    def __init__(self, *args, **kwargs):
        logger = kwargs.get("logger")
        logging_enabled = kwargs.get("logging_enabled")
        logging_level = kwargs.get("logging_level")
        self.s3_client = boto3.client('s3', aws_access_key_id=base.configdict.get(
            "AWS_CLIENT_KEY"), aws_secret_access_key=base.configdict.get("AWS_CLIENT_SECRET"))
        self.razorpay_client = razorpay.Client(
            auth=(base.configdict.get("RAZORPAY_KEY"), base.configdict.get("RAZORPAY_SECRET")))
        self.ts = URLSafeTimedSerializer(base.configdict.get("SECRET_KEY"))

    def is_from_browser(self, user_agent: str):
        if user_agent.browser in ["camino", "chrome", "firefox", "galeon", "kmeleon", "konqueror", "links", "lynx", "msie", "msn", "netscape", "opera", "safari", "seamonkey", "webkit"]:
            return True
        if user_agent.browser in ["python", "javascript"]:
            return False

        return True

    def generate_confirmation_token(self, email):
        serializer = URLSafeTimedSerializer(base.configdict.get("SECRET_KEY"))
        return serializer.dumps(email, salt=base.configdict.get("SECURITY_PASSWORD_SALT"))

    def generate_session_key(self, n_bits: int = 256):
        return random.getrandbits(n_bits)

    def confirm_token(self, token, expiration=3600):
        serializer = URLSafeTimedSerializer(
            base.configdict.get("SECURITY_PASSWORD_SALT"))
        try:
            email = serializer.loads(
                token,
                salt=base.configdict.get("SECURITY_PASSWORD_SALT"),
                max_age=expiration
            )
        except:
            return False
        return email

    def get_morphed_filename(self, email, format="txt"):
        return "{}.{}".format(hashlib.sha1(
            bytes(str(email + "-" + str(time.time())), 'utf-8')).hexdigest(), format)

    def upload_file_to_server(self, upload_filepath: list, rake, email, hand_history_format):
        print("Printing from inside")
        print(upload_filepath, rake, email, hand_history_format)
        pass

    def get_file(self, object_name, folder_name="unprocessed_hands", bucket_name="pkr-website"):
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name,
                        'Key': "{}/{}".format(folder_name, object_name)},
                ExpiresIn=3600)
        except Exception as e:
            return None
        return response
