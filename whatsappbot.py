from email import message
import json
from array import array
from operator import truediv
from tokenize import String, group
from traceback import print_list

import pywhatkit
from facebook_scraper import get_posts
from send_email import gmail_send_message

import sheets_funcs as sheets

def send_post_whatsapp(phone_num: str, post: dict):
    msg_text = post_to_plain_text(post)
    pywhatkit.sendwhatmsg_instantly(phone_num, msg_text, wait_time=5)

def send_emails(posts: array, emails: array):
    message_content = ""
    message_subject = "{x} הצעות עבודה בשבילך".format(x = len(posts))
    for post in posts:
        message_content += post_to_plain_text(post)
        message_content += "\n-----------------------------------------------\n"
    gmail_send_message(emails, message_content, message_subject, False)

def post_to_plain_text(post: dict) -> str:
    text = "נכתב על ידי {user} בתאריך {date}:".format(user = post["username"], date = post["time"]) + "\n"
    text += post["text"] + "\n" + post["post_url"]
    return text

def post_to_html(post: dict) -> str:
    html_text = "<!DOCTYPE html><html dir=rtl><body>"
    
    return html_text + "</body></html>"


def get_posts_from_group(group_id, max_pages: int = 10):
    posts = get_posts(group=group_id, pages=max_pages)
    return posts

def get_id_from_url(group_url: str) -> str:
    return group_url[group_url.find("groups") + len("groups"):].strip("/")

# searches a field's groups for posts that are relevent, according to the keywords
def find_relevent_posts(field: sheets.FIELD, pages_per_group: int = 10, max_posts: int = -1) -> array:
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
                # check if we reached max_posts
                if max_posts > 0 and len(relevent_posts) >= max_posts:
                    return relevent_posts

    return relevent_posts   

# determines if a post is relevent or not, according to keywords
def is_post_relevent(post: dict, keywords: array) -> bool:
    for keyword in keywords:
        if keyword in post["post_text"]:
            return True
    return False

def search_all_fields(max_posts: int = 10, pages_per_group: int = 10, save_to_file: bool = False) -> dict:
    results = {}
    for field in sheets.FIELD:
        relevent_posts = find_relevent_posts(field, pages_per_group, max_posts)
        if save_to_file:
            with open("{f}_posts.json".format(f = field.name), 'w', encoding="utf-8") as file:
                json.dump(relevent_posts, file, indent=4, ensure_ascii=False, default=str)
        print("found {x} relevent posts in {field}".format(x = len(relevent_posts), field = field.name))
        results[field] = relevent_posts
    return results


def main():
    with open('TECH_posts.json', 'r', encoding="utf8") as f:
        send_emails(json.load(f), ["ben.egg.gov@gmail.com"])

if __name__ == "__main__":
    main()