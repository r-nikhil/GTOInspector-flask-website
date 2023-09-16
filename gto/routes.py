from flask import make_response, render_template, request
from flask import redirect
import flask
from flask_migrate import current
from . import __base__ as base
from flask.helpers import flash
from flask_login.utils import login_user
from flask_login import logout_user, current_user, login_required
import time
import os
from werkzeug.exceptions import BadRequestKeyError
from . import app
from . import models
from . import forms
from . import db
from . import helper_functions
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from . import misc_routes
from threading import Thread


app.register_blueprint(misc_routes.misc_blueprint)
helper = helper_functions.HelperFunctions()


@app.route("/", methods=["GET", "POST"])
def index():
    resp = make_response(render_template(
        "index.html", data="Welcome to GTO Inspector", title="Home"))
    return resp


@app.route("/home")
def redir_index():
    return redirect("/")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = forms.SignUpForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        referral_code = form.referral_code.data

        user = models.User.query.filter_by(email=email).first()
        if user is not None:
            flask.flash("Something went wrong!")
            return flask.redirect(flask.url_for("signup"))
        if len(referral_code) > 0:
            coupon = models.Coupon.query.filter_by(
                coupon_code=referral_code).first()
            if coupon is None:
                flask.flash("Invalid coupon. Please register again")
                return redirect("/signup")
            coupon_type, coupon_discount_percentage, coupon_hands = coupon.get_coupon_data()

            if coupon_type == 'free_hands':
                processing_balance = coupon_hands
                discount = 0
            elif coupon_type == 'discount':
                discount = coupon_discount_percentage
                processing_balance = 0
            else:
                discount = 0
                processing_balance = 0

        # TODO: Add session key
        session_key = helper.generate_session_key()
        new_login = models.Logins(email=email, session_key=session_key,
                                  user_agent=flask.request.user_agent.browser, ip_address=flask.request.remote_addr)

        new_login_history = models.LoginHistory(
            email=email, session_key=session_key, user_agent=flask.request.user_agent.browser, ip_address=flask.request.remote_addr)

        new_user = models.User(
            name=name, email=email, password_hash=password, processing_balance=processing_balance)

        db.session.add(new_user)
        db.session.add(new_login)
        db.session.add(new_login_history)
        db.session.commit()
        flask.flash("Thank you for registering!")
        login_user(new_user)
        # TODO: Redirect to dashboard
        resp = make_response(redirect("/dashboard"))
        resp.set_cookie("session_key", str(session_key))
        resp.set_cookie("email", email)
        return resp

    return render_template("signup.html", form=form, title="Sign Up")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect("/")
    form = forms.LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        email = form.email.data

        last_login = models.Logins.query.filter_by(email=email).first()
        user = models.User.query.filter_by(email=email).first()
        if user is not None and user.check_password(password):
            login_user(user)
            current_session_key = helper.generate_session_key()
            login_history = models.LoginHistory(email=email, session_key=current_session_key,
                                                user_agent=flask.request.user_agent.browser, ip_address=flask.request.remote_addr)
            if last_login is None:
                last_login = models.Logins(email=email, session_key=current_session_key,
                                           user_agent=flask.request.user_agent.browser, ip_address=flask.request.remote_addr)
                db.session.add(last_login)
            else:
                last_login.session_key = current_session_key
            db.session.add(login_history)
            db.session.commit()

            next = flask.request.args.get("next")
            if next == None or not next[0] == '/':
                next = "/dashboard"

            resp = make_response(redirect(next))
            resp.set_cookie("email", email)
            resp.set_cookie("session_key", str(current_session_key))
            return resp

        if user is None or not user.check_password(password):
            flash("The email and password combo is wrong")

    return render_template("login.html", form=form, title="Login")


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    email = current_user.get_email()
    hero_names = ["a", "b"]
    if models.Logins.query.filter_by(email=email).first().session_key != flask.request.cookies.get("session_key"):
        logout_user()
        flash("You have been logged out!")

    password_change_form = forms.ChangePassword()
    confirm_email_form = forms.ConfirmEmail()
    return render_template("dashboard.html", user=current_user, title="Profile", password_change_form=password_change_form, confirm_email_form=confirm_email_form, hero_names=hero_names)


@app.route('/dashboard/confirm', methods=["POST"])
@login_required
def send_confirm_link():
    user_email = current_user.email
    token = helper.generate_confirmation_token(user_email)
    confirmation_link = "https://gtoinspector.poker/confirm/{token}"
    # TODO: Add mailer here and remove flash token
    # mailer.send_confirmation_mail(user_email,
    #                               current_user.first_name,
    #                               confirmation_link)
    # flash(token)
    flash("Confirmation email has been sent")
    return redirect("/dashboard")


@app.route('/confirm/<token>')
@login_required
def confirm_email(token):
    try:
        email = helper.confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.')
    user = models.User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash('Account already confirmed.')
    else:
        user.is_confirmed = True
        user.confirmation_timestamp = datetime.datetime.now()
        db.session.add(user)
        db.session.commit()
        flash('You have confirmed your account.')
    return redirect(flask.url_for('index'))


@app.route("/forgot", methods=["GET", "POST"])
def send_reset_link():
    reset_password_form = forms.ForgotPassword()

    if reset_password_form.validate_on_submit():
        user = models.User.query.filter_by(
            email=reset_password_form.email.data).first()
        if user is None:
            return render_template("/signup")
        subject = "Password reset requested"
        token = helper.ts.dumps(
            user.email, salt=app.config.get("SECURITY_PASSWORD_SALT"))
        recover_url = "https://gtoinspector.poker/reset/{token}".format(
            token=token)
        # mailer.send_password_reset_mail(user.email, recover_url)

    return render_template("forgotpassword.html", title="Forgot Password",
                           reset_password_form=reset_password_form)


@app.route('/reset/<token>', methods=["GET", "POST"])
def reset_with_token(token):
    email = helper.ts.loads(token, salt="recover-key", max_age=86400)
    form = forms.ChangeForgottenPassword()
    if flask.request.form:
        user = models.User.query.filter_by(email=email).first_or_404()
        user.password_hash = generate_password_hash(form.new_password.data)
        db.session.add(user)
        db.session.commit()
        flash("Password changed")
        if current_user.is_authenticated:
            logout_user()
        # try:
        #     mailer.send_password_change_mail(
        #         email, user.first_name, datetime.datetime.now())
        # except Exception as e:
        #     print(e)
        return redirect("/login")

    return render_template('reset_with_token.html',
                           form=form,
                           token=token,
                           title="Reset Password")


@app.route("/pricing", methods=["GET", "POST"])
def select_plan():
    try:
        user_email = current_user.get_email()
        # Checking if the user hasn't logged in from some other device
        if (models.Logins.query.filter_by(email=user_email).first().session_key) != (flask.request.cookies["session_key"]):
            logout_user()
            flash("You have been logged out!")
            return redirect("/login")
    except:
        pass
    if flask.request.form:
        resp = make_response(redirect("/payment"))
        num_hands = int(flask.request.form["num_hands"])
        price = flask.request.form["price"]
        price = float("".join(price[1:])) * 100
        resp.set_cookie("hands", str(num_hands), expires=time.time() + 5 * 60)
        resp.set_cookie("price", str(price), expires=time.time() + 5 * 60)
        resp.set_cookie("plan_currency", str("USD"))

        return resp

    return render_template("select_plan.html",
                           title="Pricing"
                           )


@app.route('/dashboard/reset_password', methods=["POST"])
def reset_password():
    password_change_form = forms.ChangePassword()
    email = current_user.get_email()
    user = models.User.query.filter_by(email=email).first()
    current_password = password_change_form.current_password.data
    if user.check_password(current_password):
        user.password_hash = generate_password_hash(
            password_change_form.new_password.data)
        db.session.commit()
        flash("Password Changed")
        # try:
        #     mailer.send_password_change_mail(
        #         email, user.first_name, datetime.datetime.now().strftime("%H:%M:%S %d/%m/%y"))
        # except:
        #     pass
        resp = make_response(redirect("/login"))
        return resp
    else:
        flash("Incorrect Password")

# TODO: Make payments more robust


@app.route("/payment", methods=["GET", "POST"])
@login_required
def payment():
    if current_user.disabled:
        logout_user()
        flash("Please contact support")
        redirect("/feedback")
    user_email = current_user.get_email()
    # Checking if the user hasn't logged in from some other device
    if (models.Logins.query.filter_by(email=user_email).first().session_key) != (flask.request.cookies["session_key"]):
        logout_user()
        flash("You have been logged out!")
        return redirect("/login")
    try:
        amount = float(flask.request.cookies["price"])
        num_hands = int(flask.request.cookies["hands"])
        plan_name = flask.request.cookies["plan_name"]
    except BadRequestKeyError as b:
        return render_template("failure.html")
    purchase_description = flask.request.cookies["plan_description"]
    plan_currency = flask.request.cookies["plan_currency"]
    return render_template("payment.html",
                           amount=amount,
                           plan_name=plan_name,
                           num_hands=num_hands,
                           purchase_description=purchase_description,
                           plan_currency=plan_currency,
                           title="Payment",
                           rzp_key=os.getenv("rzp_key")
                           )


@app.route('/charge', methods=['POST'])
def app_charge():

    amount = float(flask.request.cookies["price"])
    plan_currency = flask.request.cookies["plan_currency"]
    payment_id = flask.request.form['razorpay_payment_id']
    helper.razorpay_client.payment.capture(payment_id, amount)
    payment_info = helper.razorpay_client.payment.fetch(payment_id)
    if payment_info["captured"]:
        email = current_user.get_email()
        user = models.User.query.filter_by(email=email).first()
        coupon_used = ""
        hands = 0
        earlier_hands = user.hands_remaining
        if earlier_hands is None:
            earlier_hands = 0
        user.hands_remaining = earlier_hands + \
            int(flask.request.cookies["hands"])
        new_payment_info = models.PaymentHistory(
            payment_id=payment_info["id"],
            email=payment_info["email"],
            phone=payment_info["contact"],
            amount=payment_info["amount"],
            payment_time=payment_info["created_at"],
            payment_currency=plan_currency,
            coupon_used=coupon_used,
            hands=hands
        )
        db.session.add(new_payment_info)
        db.session.commit()
        return render_template("success.html", title="Payment Successful")
    else:
        return render_template("failure.html", title="Payment Failed")


@app.route("/payment_history")
@login_required
def payment_history():
    if current_user.disabled:
        logout_user()
        flash("Please contact support")
        redirect("/feedback")
    user_email = current_user.get_email()
    # Checking if the user hasn't logged in from some other device
    if (models.Logins.query.filter_by(email=user_email).first().session_key) != (flask.request.cookies["session_key"]):
        logout_user()
        flash("You have been logged out!")
        return redirect("/login")
    payments = models.PaymentHistory.query.filter_by(
        user_id=current_user.get_id()).all()
    for item in payments:
        item.payment_time = datetime.datetime.fromtimestamp(
            int(item.payment_time)).strftime('%H:%M:%S %p %d %B, %Y')
    return render_template("payment_history.html", payments=payments, title="Payment History")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You logged out!")
    return redirect("/login")


@app.route("/upload")
@login_required
def hand_history():
    if current_user.disabled:
        logout_user()
        flash("Please contact support")
        redirect("/feedback")
    user_email = current_user.get_email()
    confirm_email_form = forms.ConfirmEmail()
    # Checking if the user hasn't logged in from some other device
    if (models.Logins.query.filter_by(email=user_email).first().session_key) != (flask.request.cookies["session_key"]):
        logout_user()
        flash("You have been logged out!")
        return redirect("/login")
    return render_template("hand_history.html",
                           title="Hand History Upload",
                           confirm_email_form=confirm_email_form)


@app.route("/upload", methods=["POST"])
@login_required
def upload_files():
    if flask.request.files.get("filename") == "":
        flask.flash("No file uploaded")
        return redirect("/upload")

    filepath = base.configdict.get("FILE_UPLOAD_PATH")
    email = current_user.get_email()
    user = models.User.query.filter_by(email=email).first()
    if user is None:
        return redirect("/login")

    number_of_hands_remaining = user.processing_balance
    if not number_of_hands_remaining:
        flash("You do not have enough balance! Kindly recharge")
        return redirect("/pricing")
    hand_history_format = request.form.get("hhformat")
    rake = request.form.get("rake_structure")

    upload_files = request.files.getlist('file')
    if len(upload_files):
        # Combine files
        if hand_history_format == 'pokerstars':
            morphed_filename = helper.get_morphed_filename(email, "txt")
            with open(os.path.join(filepath, morphed_filename), "a+") as f:
                for upload_file in upload_files:
                    if not upload_file.filename.endswith(".txt"):
                        flash("Invalid file format")
                        return redirect("/upload")
                    upload_file.save(os.path.join(
                        filepath, upload_file.filename))
                    with open(os.path.join(filepath, upload_file.filename), "r") as tmp_f:
                        f.write("".join(tmp_f.readlines()))
                        f.write("\n\n")
                    new_file_entry = models.HandHistoryDatabase(
                        email=email, original_filename=upload_file.filename, morphed_filename=morphed_filename, file_format="txt")
                    db.session.add(new_file_entry)
        elif hand_history_format == "adda52":
            if len(upload_files) > 1:
                flask.flash(
                    "Cannot process multiple files together for Adda52 yet")
            else:
                morphed_filename = helper.get_morphed_filename(email, "pdf")
                for upload_file in upload_files:
                    upload_file.save(os.path.join(filepath, morphed_filename))
                    new_file_entry = models.HandHistoryDatabase(
                        email=email, original_filename=upload_file.filename, morphed_filename=morphed_filename, file_format="pdf")

        db.session.commit()
        thread = Thread(target=helper.upload_file_to_server, args=(
            os.path.join(filepath, morphed_filename), rake, email, hand_history_format))
        thread.start()
        # helper.upload_file_to_server(
        #     os.path.join(filepath, morphed_filename), rake, email, hand_history_format)

    else:
        flask.flash("No file selected")
        return redirect("/upload")

    return redirect("/upload")


@app.route("/previous_uploads", methods=["GET", "POST"])
@login_required
def uploaded_files():
    if current_user.disabled:
        logout_user()
        flash("Please contact support")
        redirect("/feedback")
    user_email = current_user.get_email()
    # Checking if the user hasn't logged in from some other device
    if (models.Logins.query.filter_by(email=user_email).first().session_key) != (request.cookies["session_key"]):
        logout_user()
        flash("You have been logged out!")
        return redirect("/login")
    prev_uploads = models.HandHistoryDatabase.query.filter_by(
        email=user_email).all()[::-1]
    links = []
    processed_links = []
    total_hands = []
    total_processed_hands = []
    for item in prev_uploads:
        if item.is_processed is True:
            links.append(helper.get_file(item.filename))
            processed_links.append(helper.get_file(
                item.processed_filename + "-total.csv", "processed_hands"))
            total_hands.append(item.number_of_hands)
            total_processed_hands.append(item.number_of_hands_processed)
        else:
            links.append(False)
            processed_links.append(False)
            total_hands.append(False)
            total_processed_hands.append(False)

    return render_template("previous_uploads.html",
                           prev_uploads=prev_uploads,
                           links=links,
                           processed_links=processed_links,
                           total_hands=total_hands,
                           total_processed_hands=total_processed_hands,
                           title="Previous Uploads")


@app.route("/fileQuery/", methods=["POST"])
def get_file_list():
    email = current_user.get_email()
    startdate = str(request.form['sd'])
    enddate = str(request.form['ed'])
    statement = """
SELECT morphed_filename FROM hand_history_upload WHERE "upload_timestamp" >= '%s' and "upload_timestamp" <= '%s' and email = '%s';
    """ % (
        datetime.datetime.strftime(datetime.datetime.strptime(
            startdate, "%Y-%m-%d") + datetime.timedelta(days=1), "%Y-%m-%d"),
        datetime.datetime.strftime(datetime.datetime.strptime(
            enddate, "%Y-%m-%d") + datetime.timedelta(days=1), "%Y-%m-%d"),
        email)
    files = []
    result = db.engine.execute(statement)
    for file in result:
        files.append(dict(file).get("morphed_filename"))
    if len(files):
        res = ",".join(files)
        return res
    else:
        return "file not found"


