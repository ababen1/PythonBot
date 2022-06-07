from array import array
from multiprocessing.dummy import Array
from tokenize import String
import pywhatkit
import json
from facebook_scraper import get_posts
import sheets_funcs as sheets

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
    
def get_posts_from_group(group_id, max_pages: int = 10):
    return get_posts(group=group_id, pages=max_pages)

# def get_posts_from_urls(groups_urls: array):
#     return get_posts(post_urls=groups_urls)

#send_posts("+972525563127", "postsDBProgrammers.json", 1)

print(sheets.get_spreadsheet_data("קבוצות מציאת עבודה - הייטק!A4:A"))