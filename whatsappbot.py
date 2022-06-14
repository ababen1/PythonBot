from email import message
import json
from array import array
from operator import truediv
from tokenize import String, group
from traceback import print_list
from turtle import pos

import pywhatkit
from facebook_scraper import get_posts
from send_email import gmail_send_message

import sheets_funcs as sheets

def send_whatsapp_posts(phone_num: str, post: dict):
    msg_text = posts_to_plain_text([post])
    pywhatkit.sendwhatmsg_instantly(phone_num, msg_text, wait_time=5)

def send_email_posts(posts: array, emails: array, html_text: bool = True) -> bool:
    message_subject = "{x} הצעות עבודה חדשות".format(x = len(posts))
    message_content = posts_to_html(posts) if html_text else posts_to_plain_text(posts)
    was_sent = gmail_send_message(emails, message_content, message_subject, html_text)
    print("Emails sent!" if was_sent else "Error while sending emails")

def posts_to_plain_text(posts: array) -> str:
    text = ""
    for post in posts:
        text = "נכתב על ידי {user} בתאריך {date}:".format(user = post["username"], date = post["time"]) + "\n"
        text += post["text"] + "\n" + post["post_url"]
        text += "\n--------------------------------------------------------------\n"
    return text

def posts_to_html(posts: array) -> str:
    html_text = "<!DOCTYPE html><html lang='he' dir='rtl'><body>"
    template = ""
    with open("message_template.html",  "r", encoding='utf-8') as f:
        template = f.read()
    for post in posts:
        html_text += template.format(user = post["username"], date = post["time"], content = post["text"], url = post["post_url"])
    html_text += '<h5>הודעה זו נשלחה אוטמטית ע"י מערכת מציאת עבודות של סטודיו אנטר</h5>'
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
            if is_post_relevent(post, keywords, field):
                relevent_posts.append(post)
                # check if we reached max_posts
                if max_posts > 0 and len(relevent_posts) >= max_posts:
                    return relevent_posts

    return relevent_posts   

# determines if a post is relevent or not, according to keywords
def is_post_relevent(post: dict, keywords: array, field: sheets.FIELD) -> bool:
    # Check if the post has been sent before. if it was, it's not relevent
    for sent_post in get_sent_posts(field):
        if sent_post["post_id"] == post["post_id"]:
            return False

    # Check if one of the keywords is in the post
    for keyword in keywords:
        if keyword in post["post_text"]:
            return True
    return False

def get_sent_posts(field: sheets.FIELD) -> array:
    with open("{f}_posts.json".format(f = field.name), 'r', encoding="utf-8") as file:
        return json.load(file)

def add_to_sent_posts(new_posts: array, field: sheets.FIELD):
    sent_posts = get_sent_posts(field)
    sent_posts.append(new_posts)
    with open("{f}_posts.json".format(f = field.name), 'w', encoding="utf-8") as file:
        json.dump(sent_posts, file, indent=4, ensure_ascii=False, default=str)

def search_all_fields(
    max_posts: int = 10, 
    pages_per_group: int = 10, 
    send_emails: bool = True, 
    send_whatsapps: bool = False
) -> dict:
    results = {}
    for field in sheets.FIELD:
        print("Searching for {f} jobs...".format(f = field.name))
        relevent_posts = find_relevent_posts(field, pages_per_group, max_posts)
        print("found {x} relevent posts in {field}".format(x = len(relevent_posts), field = field.name))
        was_sent = False
        if send_emails:
            was_sent =  True if send_email_posts(relevent_posts, sheets.get_emails(field)) else was_sent
        if send_whatsapps:
            # TODO: Whatsapp handling
            pass 
        if was_sent:
            add_to_sent_posts(relevent_posts, field)
        results[field] = relevent_posts
    return results


def main():
    search_all_fields(send_emails=True, max_posts=-1, pages_per_group=5)
    print("done!")

if __name__ == "__main__":
    main()