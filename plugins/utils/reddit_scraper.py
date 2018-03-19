import json
import random
import requests

class Reddit:

    class Post:
        # TODO: Do something with the author and such...
        def __init__(self, data):
            self.author = data['author']
            self.nsfw = data['over_18']
            self.url = data['url']
            self.permalink = data['permalink']

    def __init__(self, sub, limit = 100):
        self.url = f"https://www.reddit.com/r/{sub}/.json?limit={limit}"
        self.headers = { # *groan*
            'User-Agent': 'Linux:SeriousBot:v1.0.0 (by /u/ThePixeLatedCoder)'
        }

    def scrape_posts(self):
        response = requests.get(self.url, headers=self.headers).text
        data = json.loads(response)

        if len(data) == 0: return []

        # what a hacky way to do this... kms
        return [Reddit.Post(k['data']) for k in data['data']['children'] if ~k['data']['url'].endswith('/')]

    def random_url(self, posts):
        if len(posts) == 0: return ''

        random_post = random.choice(posts)

        return random_post.url




