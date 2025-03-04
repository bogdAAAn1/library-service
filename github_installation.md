## Installation from GitHub

You can install app with this instruction:

1. Clone the repository:

        git clone https://github.com/bogdAAAn1/library-service
        cd library-service

2. Create and activate a virtual environment:

       python -m venv venv
       source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. Install dependencies:

       pip install -r requirements.txt

   4. Set up environment variables:
```
    cp .env.sample .env    
    # edit .env file and add necessary credentials
```

5. Apply migrations:

        python manage.py migrate

6. Create a superuser:

       python manage.py createsuperuser


     
7. Run the development server:

        python manage.py runserver
