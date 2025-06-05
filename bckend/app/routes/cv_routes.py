from flask import Blueprint
from app.controllers.cv_controller import upload_cv, query_cv

cv_bp = Blueprint('cv', __name__)

cv_bp.route('/upload_cv', methods=['POST'])(upload_cv)
cv_bp.route('/query_cv', methods=['POST'])(query_cv)
