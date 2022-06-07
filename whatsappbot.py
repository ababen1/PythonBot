import imp
import pywhatkit
import json
import sys
sys.path.append('facebook-scraper-selenium-master\fb-scraper')


def send_posts(phone_num: str, db_path: str, max_jobs: int = 5):
    # Opening JSON file
    f = open(db_path, "r", encoding="utf8")
    posts: dict = json.load(f)
    msg_text = ""
    for i in range(len(posts)):
        if i >= max_jobs:
            break
        msg_text += list(posts.values())[i]
    f.close()
    pywhatkit.sendwhatmsg_instantly(phone_num, msg_text, wait_time=5)
    
def run_scrapper():
    pass

send_posts("+972525563127", "postsDBProgrammers.json", 1)
