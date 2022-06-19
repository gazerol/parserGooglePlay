from bs4 import BeautifulSoup
from queue import Queue
import json
import requests
import threading


def get_list_links(selected_word):
    selected_word.replace(" ", "+")
    response = requests.get(SITE + f"/store/search?q={selected_word}&c=apps")
    soup = BeautifulSoup(response.text, 'html.parser')
    try:
        main_link = soup.find(class_='Qfxief').get("href")
    except:
        main_link = None

    list_links = soup.find_all("a", class_='Si6A0c Gy4nib')

    list_format_links = [link.get("href") for link in list_links]

    if main_link is not None:
        list_format_links.insert(0, main_link)

    return list_format_links


def get_app_dict(q, selected_word):
    while True:
        link = q.get()
        url = SITE + link + "&hl=ru"
        response = requests.get(url, timeout=2)
        soup = BeautifulSoup(response.text, 'html.parser')

        name = soup.find("h1").text
        description = soup.find("div", class_="bARER").text.lower()
        q.task_done()

        if name.find(selected_word) != -1 or description.find(selected_word) != -1:
            script = soup.find("script", type="application/ld+json").text
            dict_script = json.loads(script)
            author = dict_script["author"]["name"]
            category = dict_script["applicationCategory"]

            try:
                rate = soup.find("div", class_="jILTFe").text
            except:
                rate = None

            try:
                num_rate = dict_script["aggregateRating"]["ratingCount"]
            except:
                num_rate = None

            last_update = soup.find("div", class_="xg1aie").text

            app_dict = {
                "name": name,
                "url": url,
                "author": author,
                "category": category,
                "description": description,
                "rate": rate,
                "num_rate": num_rate,
                "last_update": last_update
            }

            dict_apps[name] = app_dict


def get_dict_apps(selected_list_format_links):
    q = Queue()

    threads = [threading.Thread(target=get_app_dict, args=(q, word), daemon=True) for _ in range(20)]

    for t in threads:
        t.start()

    for link in selected_list_format_links:
        q.put(link)

    q.join()


def dict_to_json(selected_dict_apps):
    with open(f'{word}.json', 'w') as file:
        json.dump(selected_dict_apps, file, indent=4)


if __name__ == "__main__":
    SITE = "https://play.google.com"
    word = input('Еnter keyword (example "сбербанк"): ').lower()

    list_format_links = get_list_links(word)
    dict_apps = {}
    get_dict_apps(list_format_links)
    dict_to_json(dict_apps)
