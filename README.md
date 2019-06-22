# IceCube Alert App with Augmented Reality (AR)
This contains the code to process data for IceCube realtime alerts

## Installation
```
pip install -r requirements.txt
cp configs/test.json.example configs/test.json
```
* Now edit the config file. At least point the server to right address
* Set environment variable `SLACKTOKEN` to the token you get for your bot

## Running backend
```
cd backend 
gunicorn --name icebearbackend --workers 2 --user=icebear --group=icebear --daemon -w 2 -b 0.0.0.0:5000 backend:app
```
