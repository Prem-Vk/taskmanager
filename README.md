#  Taskmanager with cli access

A taskmanager with typer cli for calling crud operations , you only have to entry access-token once to perform n number of times crud operations

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

### Note: Task have four type of status
1. created - cu
2. running - ru
3. completed - co
4. failed - fa

### API access  commands

1. To signup a user `python client.py user-signup <username>`
2. To get jwt access and refresh token `python clieny.py get-jwt-token <username>`
3. for getting all tasks. Note:- Access token are require for all CRUD api calls.
   ```
   To Get all tasks:
   python client.py get-task --access-token <access token>

   To get a single task details
   python client.py get-task --access-token <access token> -t <task-id>
   ```
   <img width="1440" alt="image" src="https://github.com/user-attachments/assets/3bb39b2c-cbd6-4fe9-a2c4-b0e648f7ce1b" />
4. To create task.
   ```
   To create a task with running status and with timer set to 5. (Post 5 seconds its status will change to compeleted)
   python client.py create-task --access-token <access-token> --name '<unique task name>' --status ru --timer 5

   To create a task with created status
   python client.py create-task --access-token <access-token> --name '<unique task name>'
   ```
   <img width="1021" alt="image" src="https://github.com/user-attachments/assets/986f8531-0d7b-4194-80ea-efccc8591711" />
5. To update a task
   ```
   To Update a task and moving it to running state and change its name.
   The task status will change to completed in 5 seconds
   python client.py update-task --access-token <access-token> -t <task-id>-n '<task-name>' -s ru
   ```
   <img width="1439" alt="image" src="https://github.com/user-attachments/assets/caefdde7-c859-44bd-b458-caec2af20b57" />

6. To delete a task
   ```
   python client.py destroy-task --access-token <access-token> -t <task-id>
   ```


## Interactive cli tool
CLI tool with a loop until user exits manually to test api without using complex curl or commands

#### To run interactive mode run `python client.py run_api --access-token <access-token>`

1. To create and get task details
    <img width="1440" alt="image" src="https://github.com/user-attachments/assets/ee7885b7-f2ac-4055-b858-c4898caa9724" />
2. Update and deletion of task:
    img width="1440" alt="image" src="https://github.com/user-attachments/assets/68a30cb1-1722-456e-a65c-d71ac4f08562" />

---
# Thank You
---