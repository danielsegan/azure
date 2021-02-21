import logging
import azure.functions as func
from azure.storage.blob import BlobClient
import http.client
import json
import uuid
import urllib.parse
import os

subscriptionKey = os.environ["AzureMapsSubscriptionKey"] 
client_id =  os.environ["AzureMapsClientId"] 
conn_string = os.environ["StorageConnectionString"]  

container_name = "output"
conn = http.client.HTTPSConnection("atlas.microsoft.com")
headers = {'user-agent': "func-mapspoc", 'x-ms-client-id': f"{client_id}"}
zoom = 14
mapHeight = 1080
mapWidth = 1920

# This gets the lat/long from a text address
def resolveAddress(address):
    conn.request("GET", f"""/search/address/json?api-version=1.0&query={urllib.parse.quote(address)}&subscription-key={subscriptionKey}""", headers=headers)
    res = conn.getresponse()
    data = res.read()
    d = json.loads(data.decode("utf-8"))
    return (d["results"][0]["position"]["lat"],d["results"][0]["position"]["lon"])

# this renders the map centered on coords with a circular path drawn around the center point
def renderMap(lat,long):
    conn.request("GET", f"""/map/static/png?subscription-key={subscriptionKey}&api-version=1.0&zoom={zoom}&layer=basic&style=main&center={long}%2C{lat}&language=%7Blanguage%7D&view=Auto&height={mapHeight}&width={mapWidth}&path=lcFF0000%7Clw2%7Cla0.60%7Cra1000%7C%7C{long}%20{lat}""", headers=headers)  
    res = conn.getresponse()
    data = res.read()
    return data

def main(req: func.HttpRequest) -> func.HttpResponse:
    
    logging.info('Python HTTP trigger function processed a request.')
    name = req.params.get('address')
    
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('address')

    if name: 
        coords = resolveAddress(name)
        data = renderMap(coords[0],coords[1])

        blob_client = BlobClient.from_connection_string(conn_string, container_name=container_name, blob_name=f'{uuid.uuid4()}.png')
        blob_client.upload_blob(data)
        
        return func.HttpResponse(f"Map created for: {name}.", status_code=200)
    else: 
        return func.HttpResponse("Bad address input", status_code=400)
   