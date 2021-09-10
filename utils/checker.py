import json

# Dependencies
import requests
from lxml import html

OWL_URL = "https://overwatchleague.com/en-us/"
OWC_URL = "https://overwatchleague.com/en-us/contenders"

CONNECT_TIMEOUT = 5 
READ_TIMEOUT = 10

def check_page_islive(contenders = False):
    # Select correct url
    url = OWL_URL
    if contenders:
        url = OWC_URL

    # Get Request
    r = requests.get(url, timeout=(CONNECT_TIMEOUT,READ_TIMEOUT))
    r.raise_for_status()

    # Parse response
    root = html.fromstring(r.content)
    data = root.xpath('/html/body//script[@id="__NEXT_DATA__"]/text()')[0]
    json_data = json.loads(data)

    # Check if it's live
    blocks = json_data["props"]["pageProps"]["blocks"]
    video_player = next(filter(lambda b: "videoPlayer" in b, blocks))["videoPlayer"]

    # Check if rewards are enabled (can be optional)
    try:
        if video_player["videoLogin"][0]["enableSentinelTracking"] == 'None':
            return
    except:
        pass

    if video_player["video"]:
        if video_player["video"]["isLive"]:
            return video_player

    return

if __name__ == "__main__":
    print(check_page_islive())
    #print(check_page_islive(contenders=True))
