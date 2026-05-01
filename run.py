from app import create_app

app = create_app()

if __name__ == '__main__':
    host = app.config['FLASK_HOST']
    port = app.config['FLASK_PORT']
    debug = app.config['FLASK_DEBUG']

    app.run(host=host, port=port, debug=debug)