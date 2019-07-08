# IceCube Alert App with Augmented Reality (AR)
This contains the code to process data for IceCube realtime alerts.  
`slackcom`: Sends slack messages, firebase messages and stores events in a database.  
`backend`: Provides a REST API for querying events for the android app

## Installation
* On PROD there might be a virtual environment
```bash
cd IceCubeAlert_AR
source venv/bin/activate
```
* To install dependencies
```bash
sudo apt install sqlite3
pip install -r requirements.txt
cp configs/test.json.example configs/test.json
```
* Copy the config file .example to .json
* Now edit the config file. At least point the server to right address
* Set environment variable `SLACKTOKEN` to the token you get for your bot
* Copy the firebase token to `./configs`. File looks like `icecubear-2xxx4-firebase-adminsdk-xxx.json`

## Running backend
```bash
cd backend 
gunicorn --name icebearbackend --workers 2 --user=icebear --group=icebear --daemon -w 2 -b 0.0.0.0:5000 backend:app
```

## Event reader and database 
### Start
```bash
python slackcom.py --cfg configs/test.cfg
```
### How to delete an event from the database
`python slackcom.py --manualDeleteEvent 132454 6427419`

### How to manually insert events directly into the database
 * Copy the csv file into the events/ folder
 * Run to enter the sqlite3 console
  ```bash
  sqlite3 ./events.db
  `INSERT INTO events (run, event, event_time, e_nu, alert_type, nickname) VALUES (130033,50579430,"2017-09-22 20:54:30.436",290,"EHE-alert","170922");`
  ```  
### How to insert or update a comment for an event
 * The following command overwrites the comment in the database
 ```bash
python slackcom.py --manualAddComment 132454 6427419 "Here one can write text"
``` 