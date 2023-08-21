from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker()

def random_datetime(start_datetime, end_datetime):
    time_between_dates = end_datetime - start_datetime
    random_time = timedelta(seconds=random.randint(0, int(time_between_dates.total_seconds())))
    return start_datetime + random_time

def generate_random_message():
    timestamp = random_datetime(datetime(2018, 3, 28, 10, 26, 6), datetime(2019, 12, 5, 20, 0, 0))
    sender = fake.random_element(['Elon Musk', 'Batman', 'Mr Clean'])
    message = fake.sentence()

    return {"timestamp": timestamp, "message": f"[{timestamp.strftime('%m/%d/%y, %I:%M:%S %p')}] {sender}: {message}"}

messages = []
for _ in range(100000):
    random_message = generate_random_message()
    messages.append(random_message)

messages.sort(key=lambda x: x["timestamp"])

with open("chat.txt", "w") as output_file:
    for msg in messages:
        output_file.write(msg["message"] + "\n")