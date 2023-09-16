from flask import Blueprint, send_from_directory, render_template, request

misc_blueprint = Blueprint("misc", "misc", "static",
                           template_folder="templates")


@misc_blueprint.route("/terms", methods=["GET"])
def terms():
    return render_template("terms.html", title="Terms of Use")


@misc_blueprint.route("/privacy", methods=["GET"])
def privacy():
    return render_template("privacy.html", title="Privacy Policy")


@misc_blueprint.route('/robots.txt')
@misc_blueprint.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(misc_blueprint.static_folder, request.path[1:])


@misc_blueprint.route("/about")
def about():
    return render_template("about.html", title="About us")


@misc_blueprint.route("/cancellation")
def cancellation():
    return render_template("cancellation.html", title="Cancellation and Refund")


@misc_blueprint.errorhandler(404)
def page_not_found(e):
    return render_template("page_not_found.html", title="Not found")


@misc_blueprint.errorhandler(403)
def denied(e):
    return render_template("denied.html", title="Denied")


@misc_blueprint.errorhandler(429)
def rate_limit_exceeded(e):
    return render_template("rate_limit_exceeded.html", title="Something went wrong")
