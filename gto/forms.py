from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, DateTimeField, RadioField, SubmitField, SelectField, FileField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError


class SignUpForm(FlaskForm):
    name = StringField(
        "Name", validators=[DataRequired()], id="name")
    email = EmailField("Email", validators=[
                       DataRequired(), Email()], id="email")
    password = PasswordField("Password", validators=[DataRequired(), EqualTo(
        "confirm_password", message="Passwords must match!")], id="password")
    confirm_password = PasswordField("Confirm Password", validators=[
                                     DataRequired()], id="confirm_password")
    referral_code = StringField("Referral Code (Optional)", id="referral_code")
    submit = SubmitField("Sign Up!")


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")


class ChangePassword(FlaskForm):
    current_password = PasswordField(
        "Current Password", validators=[DataRequired()])
    new_password = PasswordField("New Password", validators=[DataRequired()])
    confirm_new_password = PasswordField(
        "Confirm New Password", validators=[DataRequired()])
    submit = SubmitField("Change")


class GoogleLogin(FlaskForm):
    submit = SubmitField("Login with Google")


class TextUploadForm(FlaskForm):
    text_file = FileField("Hand History File")
    submit = SubmitField("Upload")


class SearchForm(FlaskForm):
    hand = StringField("Hand", validators=[DataRequired()])
    submit = SubmitField("Search")


class SelectPlanForm(FlaskForm):
    plan = RadioField("Select your plan", choices=[
                      ("p5k", "5000 Hands for $50"), ("p10k", "10000 Hands for $90")])
    submit = SubmitField("Make Payment")


class ConfirmEmail(FlaskForm):
    confirm_email = SubmitField("Please confirm your email first. Click here")


class ForgotPassword(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Proceed")


class ChangeForgottenPassword(FlaskForm):
    new_password = PasswordField("New Password", validators=[DataRequired()])
    confirm_new_password = PasswordField(
        "Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Change")


########################################

###  Forms related to admin console  ###

########################################

class UserDisableForm(FlaskForm):
    disable = SubmitField("Disable")
    enable = SubmitField("Enable")


class HandUpdateForm(FlaskForm):
    type_ = SelectField("Change type",
                        choices=[
                            ("inc", "Increase"),
                            ("dec", "Decrease"),
                            ("abs", "Absolute"),
                        ])
    hands = IntegerField("Hands")
    submit = SubmitField("Update")


class AddCouponForm(FlaskForm):
    coupon = StringField("Referral Code")
    hands = IntegerField("Hands")
    submit = SubmitField("Add")


class RemoveCouponForm(FlaskForm):
    coupon = StringField("Referral Code")
    submit = SubmitField("Remove")


class EnableDisableForm(FlaskForm):
    coupon = StringField("Referral Code")
    status = SelectField("Enable/Disable",
                         choices=[
                             (True, "Enable"),
                             (False, "Disable")
                         ])
    submit = SubmitField("Change Status")
