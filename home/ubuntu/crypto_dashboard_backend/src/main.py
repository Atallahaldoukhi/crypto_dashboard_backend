from app import create_app

app = create_app()

if __name__ == '__main__':
    # Note: For deployment, a proper WSGI server like Gunicorn should be used.
    # The host '0.0.0.0' makes the server accessible externally if needed during development.
    app.run(host='0.0.0.0', port=5000, debug=True) # debug=True for development only

