from ast import parse
from calendar import c
import csv
import os
import re
import datetime
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify

#-------------------------------------------------#
# Use:                                            #
#   $env:FLASK_APP = "lentokone_backend.py"       #
#   flask run                                     #
# commands to start a server on a Windows machine.#
#-------------------------------------------------#

OPENSKY_CSV_DIRECTORY_URL = "https://opensky-network.org/datasets/metadata/"

# DO NOT change the order of COLUMNS. Used as indexed keys to get corresponding values from a csv file.
COLUMNS = [
    "icao24",
    "registration", 
    "manufacturericao",
    "manufacturername",
    "model",
    "typecode",
    "serialnumber",
    "linenumber",
    "icaoaircrafttype",
    "operator",
    "operatorcallsign",
    "operatoricao",
    "operatoriata",
    "owner",
    "testreg",
    "registered",
    "reguntil",
    "status",
    "built",
    "firstflightdate",
    "seatconfiguration",
    "engines",
    "modes",
    "adsb",
    "acars",
    "notes",
    "categoryDescription"
]

PLANES = []

app = Flask(__name__)


# --------------- file and folder handling -------------------

def get_csv_directory_html():
    response = requests.get(OPENSKY_CSV_DIRECTORY_URL)
    if(response.status_code == 200):
        return response.text

def parse_csv_paths(html):
    csv_paths = []
    soup = BeautifulSoup(html, 'html.parser')
    hrefs = soup.find_all('a')
    for href in hrefs:
        if(re.search(r"aircraftDatabase-\d\d\d\d-\d\d.csv", href.contents[0])):
            csv_paths.append(href.contents[0])
    return csv_paths

def parse_newest_csv_path_and_date(csv_paths):
    datetimes_list = []
    datetimes_and_paths = []
    for path in csv_paths:
        date = re.findall(r"\d\d\d\d-\d\d", path)
        assert(len(date) == 1)
        year, month = date[0].split("-")
        datetime_obj = datetime.datetime(int(year), int(month), 1)
        datetimes_list.append(datetime_obj)
        datetimes_and_paths.append({datetime_obj:path})
    max_date = max(datetimes_list)
    for i in datetimes_and_paths:
        for date, path in i.items():
            if(date == max_date):
                # path: string, date: datetime
                return {"path":path, "date":date}

def csv_folder_in_cwd():
    folders = os.listdir()
    if("csv" in folders):
        return True
    else:
        return False

def planes_folder_in_cwd():
    folders = os.listdir()
    if("planes" in folders):
        return True
    else:
        return False



def download_csv(local_csv_folder_path, remote_csv_file_path):
    csv_txt_content = requests.get(OPENSKY_CSV_DIRECTORY_URL+remote_csv_file_path).text
    print("File downloaded, writing to disk...")
    with open(os.path.join(local_csv_folder_path, remote_csv_file_path), 'w', encoding='UTF8') as f:
        f.write(csv_txt_content)
        f.close()
    print(f"{remote_csv_file_path} saved to {local_csv_folder_path}")

# First function to run when a server is started. Will check cwd for CSV named folder and create it, if it isn't found.
# With a CSV folder in cwd, will check it's contents and download the newest csv, if necessary. 
def initialize_csv_directory():
    cwd = os.getcwd()

    if(not csv_folder_in_cwd()):
        print(f"\n'CSV' folder not found in {cwd}. \nCreating folder 'CSV'")
        os.mkdir(os.path.join(cwd,"csv"))

    csv_folder_path = os.path.join(cwd,"csv")
    files_in_csv_folder = os.listdir(csv_folder_path)
    # Getting all csv urls from OpenSky aircraft database HTML, 
    # after which getting the filename and parsed date of the newest remote csv file in the form of {"date":datetime, "path":string}.
    newest_path_and_date = parse_newest_csv_path_and_date(parse_csv_paths(get_csv_directory_html()))

    if(len(files_in_csv_folder) == 0):
        print(f"No files detected in {csv_folder_path}")
        print(f"Downloading newest ({newest_path_and_date['date'].year}-{newest_path_and_date['date'].month}) csv file from {OPENSKY_CSV_DIRECTORY_URL}...")
        download_csv(csv_folder_path, newest_path_and_date['path'])
    else:
        print(f"Found {len(files_in_csv_folder)} files in {csv_folder_path}")
        newest_local_csv = parse_newest_csv_path_and_date(files_in_csv_folder)
        print(f"Newest local csv file dated {newest_local_csv['date']}")
        print(f"Newest remote csv file dated {newest_path_and_date['date']}")
        if(newest_local_csv['date'] == newest_path_and_date['date']):
            print(f"Newest file already in {csv_folder_path}. Continuing.")
        elif(newest_local_csv['date'] < newest_path_and_date['date']):
            print(f"Newest local file outdated. Downloading newer file from {OPENSKY_CSV_DIRECTORY_URL} ...")
            download_csv(csv_folder_path, newest_path_and_date['path'])

    return True

def initialize_planes_directory():
    cwd = os.getcwd()

    if(not planes_folder_in_cwd()):
        print(f"\n'planes' folder not found in {cwd}. \nCreating folder 'planes'")
        os.mkdir(os.path.join(cwd,"planes"))

    planes_folder_path = os.path.join(cwd,"planes")
    files_in_planes_folder = os.listdir(planes_folder_path)
    print(f"{len(files_in_planes_folder)} files in 'planes' folder")

def plane_in_planes_folder(manufacturer, model, owner):
    cwd = os.getcwd()
    planes_folder_path = os.path.join(cwd,"planes")
    files_in_planes_folder = os.listdir(planes_folder_path)
    for file_name in files_in_planes_folder:
        if file_name == f"{manufacturer}_{model}":
            return True
    return False


def get_newest_local_csv_path():
    cwd = os.getcwd()
    csv_folder_path = os.path.join(cwd,"csv")
    csv_file_paths = os.listdir(csv_folder_path)
    newest_csv = parse_newest_csv_path_and_date(csv_file_paths)
    return newest_csv['path']

# --------------------------------------


# ---------- API functions -------------
def search_by_icao24(icao24):
    for plane in PLANES:
        if(plane["icao24"] == icao24):
            return plane
    return False

def plane_data_compact(icao24):
    plane = search_by_icao24(icao24)
    plane_compact = {"manufacturername": plane["manufacturername"], "model":plane["model"], "operator":plane["operator"], "operatorcallsign": plane["operatorcallsign"], "owner":plane["owner"]}
    return plane_compact
# --------------------------------------


# -------- Flask API endpoint ----------
@app.route("/")
def get_by_icao24():
    icao24 = request.args.get("icao24")
    plane = search_by_icao24(icao24)
    if plane:
        return jsonify(plane)
    else:
        return jsonify({"ok":False})

@app.route("/image")
def get_image():
    manufacturer = request.args.get("manufacturer")
    model = request.args.get("model")

# --------------------------------------


if(initialize_csv_directory()==True):

    csv_folder_path = os.path.join(os.getcwd(),"csv")
    csv_file_path =  os.path.join(csv_folder_path, get_newest_local_csv_path())

    # Populating PLANES list with the initialized csv file's values and COLUMNS list's keys. 
    with open(csv_file_path) as csv_file:
        planes_data = csv.reader(csv_file, delimiter=',')
        for index, row in enumerate(planes_data):
            # Columns are hard coded in COLUMNS list, so skipping the first row.
            if(index != 0):
                newPlane = {}
                for index, value in enumerate(row):
                    # Row values are indexed similarly to key values in COLUMNS.
                    newPlane[COLUMNS[index]] = value
                PLANES.append(newPlane)
