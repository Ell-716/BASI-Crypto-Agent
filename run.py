from app import create_app
import os

app = create_app()

if __name__ == '__main__':

    if os.getenv('FLASK_ENV') == 'development':
        app.run(debug=True)
    else:
        app.run(debug=False)
