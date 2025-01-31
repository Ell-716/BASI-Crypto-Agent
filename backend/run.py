from backend.app import create_app
import os


config_name = os.getenv('FLASK_ENV', 'development')

app = create_app(config_name)

if __name__ == '__main__':
    app.run(debug=(config_name == 'development'))
