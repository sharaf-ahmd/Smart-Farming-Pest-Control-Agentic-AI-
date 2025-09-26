from .register import register_bp
from .login import login_bp

def init_auth(app):
    app.register_blueprint(register_bp, url_prefix="/auth")
    app.register_blueprint(login_bp, url_prefix="/auth")
