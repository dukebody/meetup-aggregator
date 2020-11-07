from datetime import datetime
import os
from copy import deepcopy
from typing import List
import json

import requests
from bs4 import BeautifulSoup
from deta import Deta


class BSCrawler():
    # Heavily based on https://github.com/python-chile/pythonchile_v2/blob/master/events/tasks.py
    def crawl_events(self, meetup_id: str) -> List[dict]:
        meetup_url = f'https://www.meetup.com/{meetup_id}/events/'
        event_list = []
        page = requests.get(meetup_url)
        if page.status_code == 200:
            soup = BeautifulSoup(page.content, 'html.parser')

            group_name = soup.find(class_="groupHomeHeader-groupNameLink").get_text()

            logo_node = soup.find(class_='avatar avatar--large') or soup.find(class_='groupHomeHeader-banner')
            group_logo = self._get_text_inside_parenthesis(logo_node.get('style'))

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
                    image = self._get_text_inside_parenthesis(image_style)
                else:
                    image = ''

                # location
                if event.find("p", class_='wrap--singleLine--truncate'):
                    location = event.find('p', class_='wrap--singleLine--truncate').get_text()
                else:
                    location = ''

                # Append event data as a dict
                event_list.append({
                    'id': url,
                    'group': {
                        'name': group_name,
                        'logo': group_logo,
                        'url': f'https://www.meetup.com/{meetup_id}/'
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

    def _get_text_inside_parenthesis(self, string: str) -> str:
        """
        Returns text inside a parenthesis.
        Example: lorem(text) -> text 
        """
        # Note: if no parenthesis will return the original string
        return string[string.find("(")+1:string.find(")")]


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

    def load_events(self):
        events = []
        with open(self.filename, 'r', encoding='utf-8') as fh:
            lines = fh.readlines()

        for line in lines:
            event = json.loads(line)
            event['date_time'] = datetime.fromisoformat(event['date_time'])
            events.append(event)

        return events


class DetaDatabase:
    def __init__(self, project_key, db_name):
        deta = Deta(project_key)
        self.db = deta.Base(db_name)

    def save_events(self, events):
        for event in events:
            event_to_insert = deepcopy(event)
            event_to_insert["date_time"] = event["date_time"].isoformat()
            self.db.put(event_to_insert, key=event_to_insert["id"])

    def load_events(self):
        events = next(self.db.fetch())

        for event in events:
            event["date_time"] = datetime.fromisoformat(event["date_time"])

        return events


def save_events(events, database):
    database.save_events(events)


def crawl_events(meetup_id, crawler):
    return crawler.crawl_events(meetup_id)


def load_events(database):
    return database.load_events()


def sort_events(events, field, reverse=False):
    return sorted(events, key=lambda event: event[field], reverse=reverse)


def get_database():
    DETA_PROJECT_KEY = os.getenv("DETA_PROJECT_KEY")
    if DETA_PROJECT_KEY:
        from utils import DetaDatabase
        return DetaDatabase(DETA_PROJECT_KEY, "events")
    else:
        from utils import FileDatabase
        return FileDatabase('events.json')