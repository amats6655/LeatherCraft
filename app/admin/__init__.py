from flask import Blueprint

admin = Blueprint('admin', __name__)

from app.admin import routes, messages_routes, hero_slides_routes, about_routes, contact_routes

