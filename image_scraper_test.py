#!/usr/bin/env python3
from bs4 import BeautifulSoup
import requests
import os
import json
import urllib.request, urllib.error, urllib.parse

def get_soup(url,header):
    return BeautifulSoup(urllib.request.urlopen(
        urllib.request.Request(url,headers=header)),
        'html.parser')

def plane_exists_in_planes(manufacturer, model, owner):
    file_name_manufacturer = manufacturer.replace(" ","_")
    file_name_model = model.replace(" ", "_")
    file_name_owner = owner.replace(" ", "_")
    file_full_name = f"{file_name_manufacturer}+{file_name_model}+{file_name_owner}.jpg"
    assert(os.path.exists("plane_imgs"))
    plane_files = os.listdir("plane_imgs")
    print(f"Plane files: {plane_files}")
    print(f"New file: {file_full_name}")
    for plane_file in plane_files:
        if plane_file == file_full_name:
            return True
    return False


def save_plane_image(manufacturer, model, owner):
    file_name_manufacturer = manufacturer.replace(" ","_")
    file_name_model = model.replace(" ", "_")
    file_name_owner = owner.replace(" ", "_")
    query = f"{file_name_manufacturer}+{file_name_model}+{file_name_owner}"
    url="http://www.bing.com/images/search?q=" + query + "&FORM=HDRSC2"

    DIR="plane_imgs"
    header={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}
    soup = get_soup(url,header)

    ActualImages=[]
    for a in soup.find_all("a",{"class":"iusc"}):
        m = json.loads(a["m"])
        murl = m["murl"]
        turl = m["turl"]

        image_name = urllib.parse.urlsplit(murl).path.split("/")[-1]

        ActualImages.append((image_name, turl, murl))

    if not os.path.exists(DIR):
        os.mkdir(DIR)

    file_name_manufacturer = manufacturer.replace(" ","_")
    file_name_model = model.replace(" ", "_")
    file_name_owner = owner.replace(" ", "_")
    FILE_NAME = f"{file_name_manufacturer}+{file_name_model}+{file_name_owner}.jpg"

    if not plane_exists_in_planes(manufacturer, model, owner):
        print("Plane file name not in 'planes. Creating a new file...")
        for i, (image_name, turl, murl) in enumerate(ActualImages):
            # TODO: Remove unnecessary loop
            if(i==0):
                try:
                    raw_img = urllib.request.urlopen(turl).read()
                    f = open(os.path.join(DIR, FILE_NAME), 'wb')
                    f.write(raw_img)
                    f.close()
                except Exception as e:
                    print("could not load : " + image_name)
                    print(e)
    else:
        print("Plane already in 'plane_imgs' folder")

#save_plane_image("Airbus","ATR 72 500","Finnair")