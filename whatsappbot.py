import json
from array import array
from operator import truediv
from tokenize import String, group
from traceback import print_list

import pywhatkit
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

def get_id_from_url(group_url: str) -> str:
    return group_url[group_url.find("groups") + len("groups"):].strip("/")

# searches a field's groups for posts that are relevent, according to the keywords
def find_relevent_posts(field: sheets.FIELD, pages_per_group: int = 10) -> array:
    relevent_posts = []
    keywords = sheets.get_keywords(field)
    # for every url in the list of groups
    for url in sheets.get_groups(field):
        current_group = get_id_from_url(url)
        print("checking group: ", current_group)
        # get posts from current url
        curent_group_posts = get_posts_from_group(current_group, pages_per_group)
        for post in curent_group_posts:
            # save the post if it's relevent
            if is_post_relevent(post, keywords):
                relevent_posts.append(post)
    return relevent_posts   

# determines if a post is relevent or not, according to keywords
def is_post_relevent(post: dict, keywords: array) -> bool:
    for keyword in keywords:
        if keyword in post["post_text"]:
            return True
    return False

for field in sheets.FIELD:
    relevent_posts = find_relevent_posts(field, 1)
    print("found {x} relevent posts in {field}".format(x = len(relevent_posts), field = field.name))