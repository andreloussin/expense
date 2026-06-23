import os
import sys
import subprocess


os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    # "config.settings_desktop"
    "config.settings"
)


import django

django.setup()


from django.core.management import call_command
from waitress import serve
from config.wsgi import application
import argparse



def initialize_database():

    print("Checking database...")
    try:
        # Migration du schema public
        call_command(
            "migrate_schemas",
            interactive=False,
            verbosity=1
        )

        print("Database ready")

    except Exception as e:
        print("Database initialization error:")
        print(e)



def main():
    parser = argparse.ArgumentParser(description="Expense Desktop Backend")
    parser.add_argument("--host", type=str, default="localhost", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8765, help="Port to bind the server to")
    args = parser.parse_args()
    
    print("Starting Expense Desktop Backend...")
    
    print("Initializing database...")   
    initialize_database()
    
    serve(
        application,
        host=args.host,
        port=args.port,
    )


if __name__ == "__main__":
    main()