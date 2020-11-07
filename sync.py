from utils import get_database, crawl_events, save_events, load_events, BSCrawler


def sync_meetups(meetup_ids):
    crawler = BSCrawler()
    database = get_database()
    events = []
    for meetup_id in meetup_ids:
        print(f"Crawling group: {meetup_id} ...")
        events += crawl_events(meetup_id, crawler)
        print("Finished")

    save_events(events, database)
    events = load_events(database)

    print(events)


if __name__ == "__main__":
    meetup_ids = ["python-barcelona", "python_alc", "PyData-Salamanca"]
    sync_meetups(meetup_ids)
