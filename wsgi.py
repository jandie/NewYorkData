from dashapp import app as application

# python gunicorn finance.wsgi:application
if __name__ == "__main__":
    application.run()
