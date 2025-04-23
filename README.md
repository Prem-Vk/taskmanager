#  Taskmanager

####  Requirements:- To run locally without docker

* Python3.10+ ---- (Beacuse latest djangov5.2 is used.)

* PostgreSQL 8.3+

* redis

OR you can simply use only `docker` to run the application

##  To Setup taskmanager application please follow below steps:

1. Clone the repo using command `git clone https://github.com/Prem-Vk/taskmanager.git`

2. Create & activate virtual env of python using below command.
```
python3.10 -m venv venv && source venv/bin/activate
```

3. Install python requirements:- `pip install -r requirements.txt`

4. Run sql script to create a database using command:- `psql < setup_postgres.sql`

5. Running Migration `python manage.py migrate --no-input` .

6. Run django server in one terminal.
```
python manage.py runserver 0.0.0.0:8000`
```
7. Run another tab of terminal for same repo location with virtual environment activated and run command
```
celery -A taskmanager worker --loglevel=info`
```

### To access api:
1. Using Typer cli:
	* Open a new terminal for same location and virtual environment activated.
	* Run command `python client.py <command>`
2. You can use curl to access api endpoints on `http://0.0.0.0:8000/api/`

### API access  commands

1. To signup a user `python client.py user-signup <username>`
2. To get jwt token `python clieny.py get-jwt-token <username>`
