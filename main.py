# import os
# from flask import Flask
# from app.extensions import db, ma, migrate, api
# from app.routes.user import blp as UserBlueprint
# # from app.routes.match_routes import blp as MatchBlueprint

# from dotenv import load_dotenv

# load_dotenv()


# def create_app():

#     app = Flask(__name__)

#     app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
#     app.config['API_TITLE'] = os.getenv('API_TITLE')
#     app.config['API_VERSION'] = os.getenv('API_VERSION')
#     app.config['OPENAPI_VERSION'] = os.getenv('OPENAPI_VERSION')
#     app.config['OPENAPI_URL_PREFIX'] = os.getenv('OPENAPI_URL_PREFIX')
#     app.config['OPENAPI_SWAGGER_UI_PATH'] = os.getenv('OPENAPI_SWAGGER_UI_PATH')
#     app.config['OPENAPI_SWAGGER_UI_URL'] = os.getenv('OPENAPI_SWAGGER_UI_URL')

#     # Init extensions
#     db.init_app(app)
#     ma.init_app(app)
#     migrate.init_app(app, db)
#     api.init_app(app)

#     # Register Blueprints
#     api.register_blueprint(UserBlueprint, url_prefix="/user")
#     # api.register_blueprint(MatchBlueprint, url_prefix="/v1/match")

#     return app

# if __name__ == "__main__":
#     app = create_app()
#     app.run(debug=True)
