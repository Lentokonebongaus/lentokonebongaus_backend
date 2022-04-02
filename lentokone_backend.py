import csv
from flask import Flask, request, jsonify


app = Flask(__name__)

columns = [
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

EXAMPLE_ICAO24 = "aaef89"
planes = []

with open('./csv/aircraftDatabase-2022-03.csv') as csvfile:
        planes_data = csv.reader(csvfile, delimiter=',')
        for index, row in enumerate(planes_data):
            if(index != 0):
                newPlane = {}
                for index, value in enumerate(row):
                    newPlane[columns[index]] = value
                planes.append(newPlane)

def search_by_icao24(icao24):
    for plane in planes:
        if(plane["icao24"] == icao24):
            return plane
    return False

def plane_data_compact(icao24):
    plane = search_by_icao24(icao24)
    plane_compact = {"manufacturername": plane["manufacturername"], "model":plane["model"], "operator":plane["operator"], "operatorcallsign": plane["operatorcallsign"], "owner":plane["owner"]}
    return plane_compact

@app.route("/")
def get_by_icao24():
    icao24 = request.args.get("icao24")
    plane = search_by_icao24(icao24)
    if plane:
        return jsonify(plane)
    else:
        return jsonify({"ok":False})
