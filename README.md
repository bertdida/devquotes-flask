# devquotes-flask

Backend source code for [devquotes.netlify.com](http://devquotes.netlify.com/). The quotes you browse are delivered from here, along with other very useful endpoints.

## Built With

- Flask
- PostgreSQL
- Firebase for authentication
- Pipenv for managing dependencies
- Heroku as hosting provider

## Local Environment

Clone this repo and install the dependencies by running:

```bash
$ git clone https://github.com/bertdida/devquotes-flask.git
$ cd devquotes-flask
$ pipenv install
```

_PostgreSQL is the database of choice for this project. You can download the community client, pgAdmin, on [this page](https://www.pgadmin.org/download/)._

Create a local database and rename [.env.example](https://github.com/bertdida/devquotes-flask/blob/master/.env.example) to remove .example and set its `SQLALCHEMY_DATABASE_URI` to your database URL.

_This project uses firebase for authentication. Therefore a firebase service account key is required. [Follow this guide](https://firebase.google.com/docs/cloud-messaging/auth-server#provide-credentials-manually) to generate a private key file in JSON format._

Inside your .env file, set the `FIREBASE_CREDENTIAL` to the path of your firebase service account key.

Activate the Pipenv shell and run the database migration.

```bash
$ pipenv shell
$ flask db upgrade
```

Start the app.

```bash
$ python run.py
```

When you have your admin user logged in on the app, you can seed the database by running.

```bash
$ flask seed
```

## Contributing

Any contributions are always welcome! If you have any problem, idea, or suggestion for the project, feel free to create issues or pull requests.

## Author

Herbert Verdida / [@bertdida](https://twitter.com/bertdida)
