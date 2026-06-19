import os
import sys
import subprocess


os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings_desktop"
)


import django

django.setup()


from django.core.management import call_command
from waitress import serve
from config.wsgi import application


def initialize_database():
    print("Checking database...")


    try:
        call_command(
            "migrate",
            interactive=False
        )

        print("Database ready")

    except Exception as e:
        print("Database initialization error:")
        print(e)



def main():

    print("Starting Expense Desktop Backend...")


    initialize_database()


    serve(
        application,
        host="127.0.0.1",
        port=8765
    )


if __name__ == "__main__":
    main()