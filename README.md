## App Installation Steps
1. Clone the repository
2. Run `python -m venv venv` to create a virtual environment
3. Run `source venv/bin/activate` to activate the virtual environment in MacOS/Linux or `venv\Scripts\activate` in Windows.
4. Run `pip install -r requirements.txt` to install the dependencies
5. Run `python manage.py makemigrations` to create migration files
6. Run `python manage.py migrate` to apply migrations
7. Run `python manage.py runserver` to run the server
8. Open `http://127.0.0.1:8000/` in your browser to view the app
