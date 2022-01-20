from flask import Flask, redirect, render_template, request

from todo_app.data.trello_items import Status, TrelloRequests
from todo_app.flask_config import Config

app = Flask(__name__)
app.config.from_object(Config())


trello_requests = TrelloRequests()


@app.route("/")
def index():
    trello_requests.init_list_maps()

    if trello_requests.errored:
        trello_requests.errored = False
        return redirect("/error")

    all_items = trello_requests.get_items()

    if trello_requests.errored:
        trello_requests.errored = False
        return redirect("/error")

    sorted_items = sorted(all_items, key=lambda item: (item.due is None, item.due))
    completed = [item for item in sorted_items if item.status == Status.COMPLETED]
    in_progress = [item for item in sorted_items if item.status == Status.IN_PROGRESS]
    not_started = [item for item in sorted_items if item.status == Status.NOT_STARTED]

    return render_template(
        "index.html",
        completed_items=completed,
        in_progress_items=in_progress,
        not_started_items=not_started,
    )


@app.route("/add-item", methods=["POST"])
def add_item_to_items():
    trello_requests.add_item(
        request.values.get("title"), request.values.get("description"), request.values.get("due-date")
    )
    return _handle_return()


@app.route("/delete-item", methods=["POST"])
def delete_item():
    trello_requests.remove_item(request.values.get("id"))
    return _handle_return()


@app.route("/complete-item", methods=["POST"])
def complete_item():
    trello_requests.update_item_status(request.values.get("id"), Status.COMPLETED)
    return _handle_return()


@app.route("/start-item", methods=["POST"])
def start_item():
    trello_requests.update_item_status(request.values.get("id"), Status.IN_PROGRESS)
    return _handle_return()


@app.route("/error")
def error_page():
    return render_template("error.html")


def _handle_return():
    if trello_requests.errored:
        trello_requests.errored = False
        return redirect("/error")
    return redirect("/")
