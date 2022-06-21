from ast import keyword
import json
import os
import dotenv
dotenv.load_dotenv()
from array import array

import pywhatkit
from facebook_scraper import get_posts
from send_email import gmail_send_message

import sheets_funcs as sheets

def send_whatsapp_posts(phone_num: str, posts: array):
    """
    Send job offers via whatsapp, using the pywhatkit package.

    Args:
        phone_num (str): the recipent's phone number
        post (array): the posts to send
    """    
    msg_text = posts_to_plain_text(posts)
    pywhatkit.sendwhatmsg_instantly(phone_num, msg_text, wait_time=5)

def send_email_posts(posts: array, emails: array, html_text: bool = True) -> bool:
    """
    Sends job offers via email.
    
    Args:
        posts (array): the facebook posts with the job offers.
        emails (array): the list of recipent emails
        html_text (bool): if true, the email will be formatted beautifuly with html. 
            otherwise, it will be ugly plain text. Defaults to true
    
    Returns:
        True if the emails were sent successfuly, or false otherwise.

    """
    if len(posts) <= 0:
        print("No posts found, no emails were sent")
        return False
    message_subject = "{x} הצעות עבודה חדשות".format(x = len(posts))
    message_content = posts_to_html(posts) if html_text else posts_to_plain_text(posts)
    was_sent = gmail_send_message(emails, message_content, message_subject, html_text)
    print("Emails sent!" if was_sent else "Error while sending emails")

def posts_to_plain_text(posts: array) -> str:
    """
    Generates a plain text message for job offers.

    Args:
        posts (array): the facebook posts with the job offers

    Returns:
        str: the plain text message formatted from the posts
    """    
    text = ""
    for post in posts:
        text = "נכתב על ידי {user} בתאריך {date}:".format(user = post["username"], date = post["time"]) + "\n"
        text += post["text"] + "\n" + post["post_url"]
        text += "\n--------------------------------------------------------------\n"
    return text

def posts_to_html(posts: array) -> str:
    """
    Generates a html text message for job offers, useful for emails.

    Args:
        posts (array): the facebook posts with the job offers

    Returns:
        str: the html formatted message
    """
    html_text = "<!DOCTYPE html><html lang='he' dir='rtl'><body>"
    template = ""
    with open("message_template.html",  "r", encoding='utf-8') as f:
        template = f.read()
    for post in posts:
        html_text += template.format(user = post["username"], date = post["time"], content = post["text"], url = post["post_url"])
    html_text += '<h5>הודעה זו נשלחה אוטמטית ע"י מערכת מציאת עבודות של סטודיו אנטר</h5>'
    return html_text + "</body></html>"

def get_posts_from_group(group_id, max_pages: int = 10, fb_credintails: tuple = None):
    """
    Gets posts from a facebook group using the facebook-scrapper package.

    Args:
        group_id (_type_): the facebook group's id.
        max_pages (int, optional): how many pages to load from the group. Defaults to 10.
        fb_credintails (tuple, optional): username and password to login to facebook with. 
            optinal, but reccomended, since not logging in may cause problems. Defaults to None.

    Returns:
        array: the list of posts scrapped from the group
    """    
    posts =[]
    try:
        posts = get_posts(group=group_id, pages=max_pages, credentials=fb_credintails)
    except Exception as error:
        print(error)

    return posts

def get_id_from_url(group_url: str) -> str:
    """
    gets a facebook group's id from its url.

    Args:
        group_url (str): the group's url

    Returns:
        str: the group's id.
    """    
    return group_url[group_url.find("groups") + len("groups"):].strip("/")

def find_relevent_posts(field: sheets.FIELD, keywords: array, pages_per_group: int = 10, max_posts: int = -1, creds: tuple = None) -> array:
    """
    searches a field's groups for posts that are relevent, according to the keywords

    Args:
        field (sheets.FIELD): the field to search, can only be one of these: TECH, SOCIAL, DESIGN, PROJECTS.
        pages_per_group (int, optional): how many pages to load for each group. Defaults to 10.
        max_posts (int, optional): the maximum amount of relevent posts to search for. -1 means no limit. Defaults to -1.
        creds (tuple, optional): Facebook username and password. Defaults to None.

    Returns:
        array: list of relevent posts
    """    
    relevent_posts = []
    # for every url in the list of groups
    for url in sheets.get_groups(field):
        current_group = get_id_from_url(url)
        print("checking group: ", current_group)
        # get posts from current url
        try:
            curent_group_posts = get_posts_from_group(current_group, pages_per_group, creds)
            for post in curent_group_posts:
                # save the post if it's relevent
                if is_post_relevent(post, keywords, field):
                    relevent_posts.append(post)
                    # check if we reached max_posts
                    if max_posts > 0 and len(relevent_posts) >= max_posts:
                        return relevent_posts
        except Exception as e:
            print(e)

    return relevent_posts   


def is_post_relevent(post: dict, keywords: array, field: sheets.FIELD, blacklist: array = []) -> bool:
    """
    Determines if a post is relevent or not. A post is relevent if it hasn't been sent before, and 
    if it has at least 1 keyword in it

    Args:
        post (dict): the post to check
        keywords (array): the list of keywords
        field (sheets.FIELD): the field that the post belongs to (can be TECH, SOCIAL, DESIGN, PROJECTS).

    Returns:
        bool: True if the post is relevent, False if not.
    """    

    for sent_post in get_sent_posts(field):
        # Check if the text is the same as other sent posts, since users repost their job offers to multiple groups
        if sent_post["post_id"] == post["post_id"] or sent_post["post_text"] == post["post_text"]:
            return False

    # Check if one of the blacklist words is in the post
    for forbbiden_word in blacklist:
        if forbbiden_word in post["post_text"]:
            return False

    # Check if one of the keywords is in the post
    for keyword in keywords:
        if keyword in post["post_text"]:
            return True
    return False

def get_sent_posts(field: sheets.FIELD) -> array:
    """
    Returns the list of posts that were sent in the past.

    Args:
        field (sheets.FIELD): the field to get the list of (can be TECH, SOCIAL, DESIGN, PROJECTS).

    Returns:
        array: list of jobs that were sent to the given field.
    """    
    with open("{f}_posts.json".format(f = field.name), 'r', encoding="utf-8") as file:
        return json.load(file)

def add_to_sent_posts(new_posts: array, field: sheets.FIELD):
    """
    Updates the list of sent posts with new posts

    Args:
        new_posts (array): the new posts there were just sent.
        field (sheets.FIELD): the field that they belong to. (can be TECH, SOCIAL, DESIGN, PROJECTS).
    """    
    sent_posts = get_sent_posts(field)
    sent_posts.append(new_posts)
    with open("{f}_posts.json".format(f = field.name), 'w', encoding="utf-8") as file:
        json.dump(sent_posts, file, indent=4, ensure_ascii=False, default=str)

def search_all_fields(
    max_posts: int = 10, 
    pages_per_group: int = 10, 
    send_emails: bool = True, 
    send_whatsapps: bool = False,
    creds: tuple = None,
    include_personal: bool = True
):
    """
    Searches for jobs for all the fields (TECH, SOCIAL, DESIGN, PROJECTS).
    See "search_field" function for more info
    """
    for field in sheets.FIELD:
        search_field(field, max_posts, pages_per_group, send_emails, send_whatsapps, creds, include_personal)

def search_personal(
    email: str, 
    max_posts: int = 10, 
    pages_per_group: int = 10,
    creds: tuple = None):
        user_data = sheets.get_user_data(email)
        if not user_data:
            print("Error: data not found for {x}. Make sure they filled the form".format(x = email))
        else:
            print("Searching for jobs for {x}...".format(x = email))
            keywords = sheets.get_keywords(user_data["field"])
            keywords.append(user_data["keywords"])
            relevent_posts = find_relevent_posts(user_data["field"], keywords, pages_per_group, max_posts, creds)
            print("found {x} relevent posts for {user}".format(x = len(relevent_posts), user = email))
            if user_data["send_email"]:
                send_email_posts(relevent_posts, [email])
            if user_data["send_whatsapp"]:
                pass #TODO
            

def search_field(
    field: sheets.FIELD,
    max_posts: int = 10, 
    pages_per_group: int = 10, 
    send_emails: bool = True, 
    send_whatsapps: bool = False,
    creds: tuple = None,
    include_personal_search: bool = True
):
    """
    Searches for jobs in a given field (TECH/SOCIAL/DESIGN/PROJECTS).

    Args:
        field (sheets.FIELD): the field to search
        max_posts (int, optional): max posts to send. Defaults to 10.
        pages_per_group (int, optional): how many pages to load for each group. Defaults to 10.
        send_emails (bool, optional): sends job offers via email if true. Defaults to True.
        send_whatsapps (bool, optional): sends job offers via whatsapp if true. Defaults to False.
        creds (tuple, optional): facebook username and password. Defaults to None.
    """

    print("Searching for {f} jobs...".format(f = field.name))
    recipents: array = sheets.get_emails(field)
    if include_personal_search:
        # Do a personal search for anyone who filled in the form
        for email in recipents:
            if sheets.get_user_data(email):
                if sheets.get_user_data(email)["field"] == field:
                    search_personal(email, max_posts, pages_per_group, creds)
                    recipents.remove(email)
    # Do a general search for anyone else
    relevent_posts = find_relevent_posts(field, sheets.get_keywords(field), pages_per_group, max_posts, creds)
    print("found {x} relevent posts in {field}".format(x = len(relevent_posts), field = field.name))
    was_sent = False
    if send_emails:
        was_sent =  True if send_email_posts(relevent_posts, sheets.get_emails(field)) else was_sent
    if send_whatsapps:
        # TODO: Whatsapp handling
        pass 
    if was_sent:
        add_to_sent_posts(relevent_posts, field)

def main():
    search_all_fields(send_emails=True, max_posts=15, pages_per_group=20, creds=(os.getenv("FB_USER"), os.getenv("FB_PASS")), include_personal=True)
    print("done!")

if __name__ == "__main__":
    main()