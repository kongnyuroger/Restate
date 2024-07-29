from app import create_app
import os

flask_app = create_app()

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    flask_app.run(host = '0.0.0.0', debug=True)