import requests
from bs4 import BeautifulSoup
import json
import re

URL = "https://just-wiped.net/rust_servers"
server_data = []
main_header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
}

while True:
    page = requests.get(URL, headers=main_header)
    soup = BeautifulSoup(page.content, "html.parser")

    for server in soup.find_all("div", class_="server"):
        server_id = server.get("id")
        server_id = server_id[7:]
        ip_header = {
            'authority': 'just-wiped.net',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
            'scheme': 'https',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'referer': f'https://just-wiped.net/rust_servers/{server_id}',
            'sec-ch-ua': 'Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': 'Windows',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'x-requested-with': 'XMLHttpRequest'
        }


        IP_URL = "https://just-wiped.net/rust_servers/" + server_id + "/connect"
        ip_page = requests.get(IP_URL, headers=ip_header)
        ip_soup = BeautifulSoup(ip_page.content, "html.parser")
        ip_and_port = re.search(r'steam://connect/(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+)', ip_soup.prettify())
        ip_and_port = ip_and_port.group(1)
        name = server.find("div", class_="name").text.strip()
        wipe = server.find("div", class_="value").find("time", class_="timeago").text.strip()
        rating = server.find("div", class_="sinfo i-rating").find("div", class_="value").text.strip()
        modded = server.find("div", class_="sinfo i-modded").find("div", class_="value").text.strip()
        player_count = server.find("div", class_="sinfo i-player").find("div", class_="value").text.strip()
        map_name = server.find("div", class_="sinfo i-map").find("div", class_="value").text.strip()
        cycle = None
        cycle_element = server.find("div", class_="sinfo i-wipe-cycle")
        if cycle_element:
            cycle = cycle_element.find("div", class_="value").text.strip()
        server_flag = server.find("div", class_="server-flag").get("title")
        max_group = None
        max_group_element = server.find("div", class_="sinfo i-max-group")
        if max_group_element:
            max_group = max_group_element.find("div", class_="value").text.strip()
        difficulty = None
        wipe_schedule = None
        tag_line_element = server.find("div", class_="tags")
        if tag_line_element:
            difficulty_element = tag_line_element.find("div", class_="tag browser_tag",
                                                       title=lambda x: x and "difficulty" in x)
            if difficulty_element:
                difficulty = difficulty_element.text.strip()
            wipe_schedule_element = tag_line_element.find("div", class_="tag browser_tag",
                                                          title=lambda x: x and "wipe schedule" in x)
            if wipe_schedule_element:
                wipe_schedule = wipe_schedule_element.text.strip()

        is_official = False
        official_tag = tag_line_element.find("div", class_="tag official",
                                             title=lambda x: x and "This is an official Rust server!" in x)
        if official_tag and official_tag.text.strip() == "Official":
            is_official = True

        server_data.append({
            "name": name,
            "wipe": wipe,
            "rating": rating,
            "modded": modded,
            "player_count": player_count,
            "map_name": map_name,
            "cycle": cycle,
            "server_flag": server_flag,
            "max_group": max_group,
            "difficulty": difficulty,
            "wipe_schedule": wipe_schedule,
            "isOfficial": is_official,
            "serverIp": ip_and_port
        })

    next_button = soup.find("span", class_="next").find("a")
    if not next_button:
        break
    URL = "https://just-wiped.net" + next_button["href"]

    with open("serversList.json", "w") as outfile:
        # Write the data to the file in JSON format
        json.dump(server_data, outfile)