# Lentokonebongaus-backend


Lentokonebongaus-backend serves lentokonebongaus-frontend (Airplane GO) through a Flask API by sending a JSON response containing plane model, manufacturer, owner and other plane details that can't be fetched from The OpenSky Network's API. Lentokonebongaus-backend can also be used as a stand-alone REST API at http://172.105.80.249?icao24={???}.

## Inner workings
Lentokonebongaus-backend is run on a Flask server, and when the server recieves a get request with an URL parameter of "icao24", it will search through a CSV file to link the icao24 code to plane details, which the server will then return as a JSON. If no plane details are found, the server will return a JSON containing *{ok:false}* instead.

The backend uses automatically downloaded CSV file from https://opensky-network.org/datasets/metadata/. Everytime the Flask server is started, lentokonebongaus-backend will fetch a list of CSV filenames from OpenSky Network, parse dates from those filenames, find the newest remote CSV file, check whether the current local CVS file is up to date, and download and replace the newest CSV file if an older file exists locally or doesn't exist at all.

####  Possible directions for future development

Airplane GO currently uses Azure to search for a URL of a plane picture corresponding to plane details fetched from backend, but lentokonebongaus-backend also contains a commented out function for automatically searching and downloading relevant plane pictures to seperate local folders. Firstly, this could be used as way to not use Azure. Secondly, by having the pictures stored locally for any given plane model, manufacturer and owner combination, there could be greater control over the images displayed in Airplane Go.

Storing and sending images on top of sorting through a large CSV file proved to be too much for Linode's Nanode server, so the feature isn't implemented in the final version. With a more powerfull server, storing pictures locally could be a viable solution though.
