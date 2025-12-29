import os
from flask import Flask
from dotenv import load_dotenv
from flask_cors import CORS  # <-- import at the top


from app.utils.helpers import setupLambdaLogger, setupLogger

from .extensions import db, ma, migrate, api



# from .models import User, Project, Task  # list all models here

from .routes.user import blp as UserBlueprint
from .routes.organization import blp as OrgBlueprint
from .routes.project import blp as ProjectBlueprint
from .routes.timesheet import blp as TimesheetBlueprint
from .routes.reports import blp as ReportsBlueprint


def create_app():
    load_dotenv()  # <-- Load .env variables

    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # setupLogger(app)
    setupLambdaLogger(app)

    # Database
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'False') == 'True'

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['ACCESS_TOKEN_EXPIRE_TIME'] = os.getenv('ACCESS_TOKEN_EXPIRE_TIME', '3600')
    app.config['REFRESH_TOKEN_EXPIRE_SECONDS'] = os.getenv('REFRESH_TOKEN_EXPIRE_SECONDS', '36000')

    # API / Swagger
    app.config['API_TITLE'] = os.getenv('API_TITLE', "Timesheet API")
    app.config['API_VERSION'] = os.getenv('API_VERSION', "1.0")
    app.config['OPENAPI_VERSION'] = os.getenv('OPENAPI_VERSION', "3.0.3")
    app.config['OPENAPI_URL_PREFIX'] = os.getenv('OPENAPI_URL_PREFIX', "/")
    app.config['OPENAPI_SWAGGER_UI_PATH'] = os.getenv('OPENAPI_SWAGGER_UI_PATH', "/swagger")
    app.config['OPENAPI_SWAGGER_UI_URL'] = os.getenv('OPENAPI_SWAGGER_UI_URL')


    app.config['APP_EMAIL_ADDRESS'] = os.getenv('APP_EMAIL_ADDRESS')
    app.config['APP_EMAIL_ADDRESS_PASSWORD'] = os.getenv('APP_EMAIL_ADDRESS_PASSWORD')
    app.config['LOGIN_URL'] = os.getenv('LOGIN_URL')
    app.config['HR_EMAIL'] = os.getenv('HR_EMAIL')
    app.config['HR_PHONE'] = os.getenv('HR_PHONE')

    # Init extensions
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    api.init_app(app)

    # Blueprints
    api.register_blueprint(OrgBlueprint, url_prefix="/organization")
    api.register_blueprint(UserBlueprint, url_prefix="/user")
    api.register_blueprint(ProjectBlueprint, url_prefix="/project")
    api.register_blueprint(TimesheetBlueprint, url_prefix="/timesheet")
    api.register_blueprint(ReportsBlueprint, url_prefix="/reports")


    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)