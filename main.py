from flask import Flask, render_template
from applications.model import db
import os

FOLD = 'static/proofs/'

    
def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///D:/Users/karpa/Pappu/IITM/MAD_proj/code/householdServices.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
    app.config['UPLOAD_FOLDER'] = FOLD

    app.secret_key = os.urandom(24)
    db.init_app(app)
    try:
        with app.app_context():
            db.create_all()
            print("Database initialized successfully.")
    except Exception as e:
        print(f"Error {e}")
    return app

app = create_app()


@app.route('/')
def homepage():
    return render_template('homepage.html')

if __name__ == '__main__':
    from applications.controller import *
    app.run(debug=True)