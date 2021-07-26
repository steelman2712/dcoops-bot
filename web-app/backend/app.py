from flask import Flask, request, redirect, session

# import os
# from steelforge_site_utils.aws_verify import verify_jwt, authed, get_user_type, verify_access_token

SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")

app = Flask(__name__)
# app.secret_key = SECRET_KEY
dcoops = Blueprint("dcoops", __name__)
app.register_blueprint(dcoops, url_prefix="/dcoops")

print("Started")


@dcoops.route("/hello-world", methods=["GET"])
def hello_world():
    return "ping"


@dcoops.route("/ping", methods=["GET"])
def ping():
    return "ping"
