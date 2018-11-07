import requests
import whois
import builtwith
import sys
import os
import datetime
from bs4 import BeautifulSoup


#class with the information extracted from details url
class DetailedFlight:
    company = ""
    flight = ""
    terminal = ""
    status = ""
    date = ""
    arrival = ""
    real_arrival_time = ""
    origin = ""
    iata = ""
    departure_date = ""
    departure_time= ""
    departure_real_time = ""
    flight_url = ""



def saveLine(newLine):
    newLine = newLine.encode(sys.stdout.encoding, errors='replace')
    with open(filename, "ab") as myfile:
        myfile.write(newLine)
        myfile.close()

def saveDetails(details):
    newLine = details.company + ";" + details.flight + ";" + details.terminal + ";" + details.status + ";" + details.date + ";" + details.arrival + ";" + details.real_arrival_time + ";" + details.origin + ";" + details.iata + ";" + details.departure_date + ";" + details.departure_time + ";" + details.departure_real_time+"\n"
    saveLine(newLine)

def getRow(row):
    if (not row.ins):  # prevent ads
        details = DetailedFlight()
        details.date = date
        details.origin = row.find(id="fdest").b.string

        if (row.find(id="fdest").find("a")):
            details.iata = row.find(id="fdest").find("a").string
        else: #in case iata isn't a link
            dest = row.find(id="fdest")
            details.iata= row.find(id="fdest").contents[1][3:-3]

        if (row.find(id="fair").a):
            details.company = row.find(id="fair").a.string
        else:
            details.company = row.find(id="fair").string
        details.flight = row.find(id="fnum").a.string
        details.arrival = row.find(id="fhour").a.string

        #get terminal, could be empty if not landed
        if (row.find(id="fterm")):
            details.terminal = row.find(id="fterm").string
        if (details.terminal == None):
            details.terminal = ""

        #get flight status, changes id depending div color:
        row_status = ""
        if (row.find(id="fstatus_Y")): #yellow
            row_status = row.find(id="fstatus_Y")
        if (row.find(id="fstatus_G")): #green
            row_status = row.find(id="fstatus_G")
        if (row.find(id="fstatus_GR")): #grey
            row_status = row.find(id="fstatus_GR")
        if (row.find(id="fstatus_R")): #red
            row_status = row.find(id="fstatus_R")
        if (row.find(id="fstatus_O")): #orange
            row_status = row.find(id="fstatus_O")


        if (not row_status == ""):
            details.status = row_status.a.string
            details.flight_url = row_status.a.get("href")

        details.status = details.status[:-4] #delete [+] from the string
        real_arrival = details.arrival #by default, if flight on time, the arrival time is also the real arrival time.

        # get detailed information from the flight:
        details = getDetailInfo(base_url+details.flight_url, details)

        #save details into new line:
        saveDetails(details)



def getDetailInfo(urldetail, details):
    soup = getUrl(urldetail)

    arrival_div = soup.find(id="flight_info").find(id="flight_arr")
    details.real_arrival_time = arrival_div.h2.string


    dep_div = soup.find(id="flight_info").find(id="flight_dep").span.br

    if not dep_div.contents :
        dep_div = soup.find(id="flight_info").find(id="flight_dep").span

    #for e in dep_div.findAll('br'):
     #   e.extract()

    for content in dep_div.contents:
        if content.string:
            if "Fecha:" in content.string: # departure date
                details.departure_date = content.string[7:]
            if "Salió a las:" in content.string:
                details.departure_real_time = content.string[13:]
            if "Hora planificada de salida:" in content.string:
                details.departure_time = content.string[28:]
        else:
            if content.name=="b":
                if "Fecha:" in content.contents[0].string:  # departure date
                    details.departure_date = content.contents[0].string[7:]
                if "Salió a las:" in content.contents[0].string:
                    details.departure_real_time = content.contents[0].string[13:]
                if "Hora planificada de salida:" in content.contents[0].string:
                    details.departure_time = content.contents[0].string[28:]
    return details

def getUrl(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    return soup

def getData(url):
    soup = getUrl(url)
    #find divs with id=flight_detail, are the ones with the info.
    table = soup.findAll(id='flight_detail')

    for row in table:
        getRow(row)


#settings:
now = datetime.datetime.now()
date = now.strftime("%Y-%m-%d") #current date
filename="flights_barcelona.csv"
base_url="https://www.barcelona-airport.com"
url = base_url+"/esp/llegadas-aeropuerto-barcelona.php?tp="
print (whois.whois(base_url))
print(builtwith.builtwith(base_url))

#delete .csv if exists:
if os.path.exists(filename):
    os.remove(filename)

#create header on file:
newLine = "Company" + ";" + "Flight" + ";" + "Terminal" + ";" + "Status" + ";" + "Date" + ";" + "Arrival" + ";" + "Real_Arrival"+ ";" + "Origin" + ";" + "IATA" + ";" +"Departure" + ";" + "Departure_time" + ";" + "Departure_real_time" + "\n"
saveLine(newLine)

#get flights from 00:00 to 06:00
print("get flights from 00:00 to 06:00")
getData(url+"0")
#get flights from 06:00 to 12:00
print("get flights from 06:00 to 12:00")
getData(url+"6")
#get flights from 12:00 to 18:00
print("get flights from 12:00 to 18:00")
getData(url+"12")
#get flights from 18:00 to 24:00
print("get flights from 18:00 to 24:00")
getData(url+"18")




