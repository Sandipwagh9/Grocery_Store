from flask import Flask
# from flask_migrate import Migrate

from application.database import db
import os

curr_dir=os.path.abspath(os.path.dirname(__file__))
def create_app():
    app=Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///"+os.path.join(curr_dir,"database.db")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'static'
    app.secret_key = "secret"

    db.init_app(app)
    # migrate = Migrate(app, db)
    app.app_context().push()

    return app

app = create_app()

from application.controllers import *

if __name__=='__main__':
    db.create_all()
    app.run(debug=True) 