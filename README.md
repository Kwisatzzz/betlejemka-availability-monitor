# Betlejemka's availability monitor
Times are tough. Many affluent individuals are unsure how to spend their leisure time, so they follow social media trends: they go hiking. Unfortunately, we, the true adventurers and sports enthusiasts, often find ourselves unable to book rooms because they're fully reserved. This script will notify you as soon as (or rather, according to the *checking_interval* parameter) a booking slot at Betlejemka's mountain lodge becomes available.

## Setup
Run:
```bash
./setup.sh
```

## Config file
The script uses configuration files in YAML format. Here’s an example:
```
checking_interval: 300
target_date: "12-13-2024"

email_config:
  subject: "wolne pokoje" 
  body: "W betlejemce są wolne pokoje"
  from_email: ""
  from_password: ""
  recipients: ["example@gmail.com", "another.example@gmail.com"]
```
- *from_email* parameter is your Gmail address.
- To send an email via your Google account, you need to create an app password. [Here is the official instruction](https://support.google.com/mail/answer/185833?hl=en). Enter the app password in the from_password parameter.

## Usage
The simplest way to use the script is to fill in the `config.yaml` file and run the script, which will use it by default:
```bash
source .venv/bin/activate
python3 app.py
```

You will see logs like this:
```
2024-12-10 00:29:53,169 - INFO - The date 12-20-2024 is not available.
```
The script will check availability every N seconds, as defined by the checking_interval parameter. When the desired date becomes available for booking, you’ll see the following logs:
```
2024-12-10 00:32:50,053 - INFO - The date 12-13-2024 is available!
2024-12-10 00:32:51,234 - INFO - Email sent successfully!
```

You can set multiple recipients in the configuration file to notify multiple people.

## What does this amazing script actually look for?
Betlejemka uses a fancy API to manage bookings for their lodge. The data is available in JSON format, and the script checks it for availability. Here's an example of what the API response might look like:
```JSON
"12-12-2024": {
  "status": "simple",
  "text": "",
  "price": 75,
  "minLength": 1,
  "canstart": true,
  "canend": true,
  "lengthType": "minimal",
  "minDayTo": "12-13-2024",
  "maxLength": 28
},
"12-13-2024": {
  "status": "disabled",
  "text": "",
  "price": 0,
  "minLength": 1,
  "canstart": false,
  "canend": true,
  "minDayTo": "12-14-2024",
  "maxLength": 28
}
```
In simple terms:
- If the status is "simple", the date is open for booking.
- Otherwise, it’s not available.