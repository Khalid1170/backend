from flask import Blueprint, send_from_directory
import os

static_bp = Blueprint("static_bp", __name__)

@static_bp.route("/uploads/<filename>")
def uploads(filename):
    path = os.path.join(os.getcwd(), "backend/static/uploads")
    return send_from_directory(path, filename)

@static_bp.route("/qrcodes/<filename>")
def qrcodes(filename):
    path = os.path.join(os.getcwd(), "backend/static/qrcodes")
    return send_from_directory(path, filename)