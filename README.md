# Survey Backend
This app contains the backend code to send invitations to the contact tracing survey, as well as process survey results.

## Running locally
The app uses pipenv to manage python dependencies, and Docker + docker-compose to manage running the server and DB. To get started:

Set environment variables
```bash
cp backend.env .env
```

Fill in the empty variables in the `.env` file to be able to run the full backend.

Run the DB and Django app in Docker:
```bash
docker-compose build
docker-compose up
```

Then go to `http://127.0.0.1:8000/` to see the app in action.

## Development
When you make a change to models, update the migrations with:
```bash
pipenv run python manage.py makemigrations
```

Add dependencies:
`pipenv install <dep>` 


## Admin interface
Using the admin interface:
```bash
pipenv run python manage.py createsuperuser
```
Then go to `localhost:8000/admin`

TODO: setting up + testing Webhooks
