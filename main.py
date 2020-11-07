from datetime import datetime
from typing import List
import json

import requests
from bs4 import BeautifulSoup


class BSCrawler():
    def crawl_events(self, meetup_id: str) -> List[dict]:
        # get html page
        meetup_url = f'https://www.meetup.com/{meetup_id}/events/past/'

        # Stolen from https://github.com/python-chile/pythonchile_v2/blob/master/events/tasks.py
        # Call meetup_url
        event_list = []
        page = requests.get(meetup_url)
        if page.status_code == 200:
            # Parse page
            soup = BeautifulSoup(page.content, 'html.parser')

            group_name = soup.find(class_="groupHomeHeader-groupNameLink").get_text()
            group_logo = self.get_image_from_background_image(soup.find(class_='avatar avatar--large').get('style'))

            events = soup.findAll('li', 'list-item border--none')
            for event in events:
                name = event.find(class_='eventCardHead--title').get_text()
                date_time = datetime.fromtimestamp(int(event.find('time').get('datetime')) / 1000)

                if len(event.findAll(class_='text--small padding--top margin--halfBottom')) > 0: 
                    description = event.findAll(class_='text--small padding--top margin--halfBottom')[1].get_text()
                else:
                    description = ''

                url = 'https://www.meetup.com' + event.find(class_='eventCard--link').get('href')

                # Check if event haves an image
                if event.find(class_='eventCardHead--photo'):
                    image_style = event.find(class_='eventCardHead--photo').get('style')
                    image = self.get_image_from_background_image(image_style)
                else:
                    image = ''

                # location
                if event.find("p", class_='wrap--singleLine--truncate'):
                    location = event.find('p', class_='wrap--singleLine--truncate').get_text()
                else:
                    location = ''

                # Append event data as a dict
                event_list.append({
                    'group': {
                        'name': group_name,
                        'logo': group_logo
                    },
                    'name': name,
                    'date_time': date_time,
                    'url': url,
                    'image': image,
                    'description': description,
                    'location': location
                })
            return event_list

        else:
            raise Exception(f'Got code: {page.status_code} parsing {url}')

    def get_image_from_background_image(self, background_image: str) -> str:
        return background_image.lstrip('background-image:url()').rstrip(')')


class FileDatabase:
    def __init__(self, filename):
        self.filename = filename

    @staticmethod
    def json_converter(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()

    def save_events(self, events):
        with open(self.filename, 'w', encoding='utf-8') as fh:
            events_as_json = [json.dumps(event, default=self.json_converter) for event in events]
            for event_json in events_as_json:
                fh.write(event_json + '\n')

    def load_events(self, sort_by_dt=False):
        events = []
        with open(self.filename, 'r', encoding='utf-8') as fh:
            lines = fh.readlines()

        for line in lines:
            event = json.loads(line)
            event['date_time'] = datetime.fromisoformat(event['date_time'])
            events.append(event)

        if sort_by_dt:
            events = sorted(events, key=lambda event: event['date_time'], reverse=True)

        return events


def save_events(events, database):
    database.save_events(events)


def crawl_events(meetup_id, crawler):
    return crawler.crawl_events(meetup_id)


def load_events(database, sort_by_dt=False):
    return database.load_events(sort_by_dt)


if __name__ == "__main__":
    meetup_ids = ["python-barcelona", "python_alc"]

    crawler = BSCrawler()
    database = FileDatabase('events.json')

    events = []
    for meetup_id in meetup_ids:
        print(f"Crawling group: {meetup_id} ...")

        events += crawl_events(meetup_id, crawler)

        print(f"Finished")

    save_events(events, database)
    events = load_events(database)

    print(events)