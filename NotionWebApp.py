# import tkinter as tk
from datetime import datetime, timezone,date
import requests
from flask import Flask, request,render_template
import json
app = Flask(__name__)


NOTION_TOKEN = ""

DATABASE_ID_habits = ""
DATABASE_ID_prayers = ""
DATABASE_ID_Habits_avoided = ""
DATABASE_ID_meals = ""
DATABASE_ID_dhikr = ""
DATABASE_ID_for_you = ""


headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}


page_id_change= ''

def get_pages(DatabaseID,num_pages=None):

    url = f"https://api.notion.com/v1/databases/{DatabaseID}/query"

    get_all = num_pages is None
    page_size = 100 if get_all else num_pages

    payload = {"page_size": page_size}
    response = requests.post(url, json=payload, headers=headers)

    data = response.json()

    """if you want to dump data , uncomment this code"""
    # with open('db.json', 'w', encoding='utf8') as f:
    #    json.dump(data, f, ensure_ascii=False, indent=4)

    results = data["results"]
    while data["has_more"] and get_all:
        payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
        url = f"https://api.notion.com/v1/databases/{DatabaseID}/query"
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        results.extend(data["results"])

    return results


def get_information(DatabaseID):
    day = str(datetime.now().day)
    day = "0" + day if len(day) == 1 else day
    Habits_pages = get_pages(DatabaseID)
    NumberOfPages=len(Habits_pages)

    if NumberOfPages ==0:
        return None
    Columns = Habits_pages[0]["properties"].keys()
    if NumberOfPages != 0:
        props = Habits_pages[0]["properties"]
        published = str(props["Date"]["date"]["start"]).split("-")[-1].split("T")[0]
        page_id_change = Habits_pages[0]["id"] if day == published else ""
        return {"NumberOfPages":NumberOfPages,"Columns":Columns,"page_id_change":page_id_change}

    return {"NumberOfPages": NumberOfPages, "Columns": Columns, "page_id_change": None}


habits_informations=get_information(DATABASE_ID_habits)
if habits_informations is not None:
    print("NumberOfPages: ",habits_informations["NumberOfPages"])
    print("Columns: ",list(habits_informations["Columns"])[:-1])
    if habits_informations["page_id_change"]!=None:
        page_id_change=habits_informations["page_id_change"]

def create_page(data: dict,DATABASE_ID):
    """create a new row (page)"""
    create_url = "https://api.notion.com/v1/pages"

    payload = {"parent": {"database_id": DATABASE_ID}, "properties": data}

    res = requests.post(create_url, headers=headers, json=payload)
    print(res.status_code)
    return res

def update_page(page_id: str, data: dict):
    """update on existing row"""
    url = f"https://api.notion.com/v1/pages/{page_id}"

    payload = {"properties": data}

    res = requests.patch(url, json=payload, headers=headers)
    return res


@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'POST':

        # habits
        habit_1 = True if request.form.get('habit_1')!=None else False
        habit_2 = True if request.form.get('habit_2') != None else False
        habit_3 = True if request.form.get('habit_3')!=None else False
        habit_4 = True if request.form.get('habit_4')!=None else False
        habit_5 = True if request.form.get('habit_5')!=None else False
        habit_6 =True if request.form.get('habit_6')!=None else False
        habit_7 =True if request.form.get('habit_7')!=None else False



        habits_data = {
            "Date": {"date": {"start": date, "end": None}},
            "habit_1": {"checkbox": habit_1},
            "habit_2": {"checkbox": habit_2},
            "habit_3": {"checkbox": habit_3},
            "habit_4": {"checkbox": habit_4},
            "habit_5": {"checkbox": habit_5},
            "habit_6": {"checkbox": habit_6},
            "habit_7": {"checkbox": habit_7}
        }



        if len(page_id_change) != 0:
            print("update")
            print("page_id_change: ", page_id_change)
            update_page(page_id_change, habits_data)

        else:
            print("cerete")
            create_page(habits_data,DATABASE_ID_habits)


        return render_template(r"index3.html")

    else:
        return render_template(r"index3.html")


if __name__ == '__main__':

    app.run(debug=True)

