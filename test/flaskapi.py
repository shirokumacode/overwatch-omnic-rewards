from flask import Flask, Response, json, request

with open("Live.html", 'r') as f:
    live_html = f.read()

with open("NotLive.html", 'r') as f:
    notlive_html = f.read()

continue_tracking = {"status": 200, "data": {"continueTracking": True}}
stop_tracking = {"status": 200, "data": {"continueTracking": False}}

global watch_min
watch_min = 1

api = Flask(__name__)


@api.route('/owlpage', methods=['GET'])
def get_owlpage():
    return_page = live_html
    #return_page = notlive_html
    return return_page


@api.route('/owcpage', methods=['GET'])
def get_owcpage():
    #return_page = live_html
    return_page = notlive_html
    return return_page


@api.route('/owl', methods=['OPTIONS', 'POST'])
def owl_tracking():
    global watch_min
    if request.method == 'OPTIONS':
        return Response(status=200)
    if request.method == 'POST':
        if watch_min > 0:
            watch_min = watch_min - 1
            return json.jsonify(continue_tracking)
        else:
            return json.jsonify(stop_tracking)


@api.route('/owc', methods=['OPTIONS', 'POST'])
def owc_tracking():
    global watch_min
    if request.method == 'OPTIONS':
        return Response(status=200)
    if request.method == 'POST':
        if watch_min > 0:
            watch_min = watch_min - 1
            return json.jsonify(continue_tracking)
        else:
            return json.jsonify(stop_tracking)


if __name__ == '__main__':
    api.run()
