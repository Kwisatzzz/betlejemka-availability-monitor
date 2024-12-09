import argparse
import json
import logging
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)


def send_email_gmail(subject, body, to_email, from_email, from_password):
    """
    Sends an email using Gmail.

    :param subject: Subject of the email.
    :param body: Body of the email.
    :param to_email: Recipient email address.
    :param from_email: Sender email address (your Gmail account).
    :param from_password: Sender email password or app password.
    """
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(from_email, from_password)
            server.sendmail(from_email, to_email, msg.as_string())
            logging.info("Email sent successfully!")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")


def fetch_calendar_data():
    url = "https://engine9616.idobooking.com/index.php"

    params = {
        "module": "dayevents",
        "_": "1733674072294",
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": "https://engine9616.idobooking.com/",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        logging.error(f"Failed to fetch data. Status code: {response.status_code}")
        return None
    try:
        return response.json()
    except json.JSONDecodeError:
        logging.error("Failed to parse JSON response.")
        return None


def check_date_availability(data, date_to_check):
    if date_to_check in data["eventdays"]:
        date_info = data["eventdays"][date_to_check]
        if date_info["status"] == "simple" and date_info["canstart"]:
            return True
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="An application for monitoring Betlejemka's rooms availability."
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to application's config file.",
    )
    args = parser.parse_args()

    with open(args.config, "r") as file:
        config = yaml.safe_load(file)

    while True:
        calendar_data = fetch_calendar_data()
        if calendar_data:
            if check_date_availability(calendar_data, config["target_date"]):
                logging.info(f"The date {config['target_date']} is available!")
                for recipient in config["email_config"]["recipients"]:
                    send_email_gmail(
                        config["email_config"]["subject"],
                        config["email_config"]["body"],
                        recipient,
                        config["email_config"]["from_email"],
                        config["email_config"]["from_password"],
                    )
                break
            else:
                logging.info(f"The date {config['target_date']} is not available.")
                time.sleep(config["checking_interval"])
        else:
            logging.error("Failed to retrieve calendar data.")
