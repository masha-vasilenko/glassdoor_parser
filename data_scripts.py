import json
import requests
import logging
import logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('scripts')


with open('reviews.json', 'r') as f:
    reviews = json.loads(f.read())


for review in reviews[:10]:
    r = requests.post('https://gdreviews.herokuapp.com/api/reviews/',
                      json=review)
    if r.status_code == 201:
        logger.info(f"Success: {review['company']} - {review['role']}")
    else:
        logger.error(f"Failure: {r.status_code} - {r.text} {review['company']}")
