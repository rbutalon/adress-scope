from flask import Blueprint, current_app, jsonify, render_template

from .ip_handler import collect_ip_info

main = Blueprint("main", __name__)


@main.get("/")
def index():
    return render_template("index.html")


@main.get("/about")
def about():
    return render_template("about.html")


@main.get("/api/ip-info")
def ip_info():
    result = collect_ip_info()
    status = 200 if result["success"] else 503
    return jsonify(result), status
