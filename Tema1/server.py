import json
import requests
import time
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler


def writeToLogFile(response):
    info = json.loads(open("logs.json").read())
    info.append(response)
    open("logs.json", "w").write(json.dumps(info))


def getLatLongFromCityName(cityName):
    startTime = time.time()
    key = json.loads(open("conf.json").read())
    url = "https://api.opencagedata.com/geocode/v1/json?q=" + cityName + "&key=" + key['OpenCageAPIKey'] + "&language=ro&pretty=1"
    response = requests.get(url)
    if response.ok:
        endTime = time.time()
        info = {"API": "OpenCageData", "Request": url, "Response": response.status_code, "Latency": (endTime - startTime)}
        writeToLogFile(info)
        return {"response": response, "result": response.json()['results'][0]["geometry"]}
    else:
        endTime = time.time()
        info = {"API": "OpenCageData", "Request": url, "Response": response.status_code, "Latency": (endTime - startTime)}
        writeToLogFile(info)
        return False


def getWeatherFromLatLong(coordinates):
    startTime = time.time()
    key = json.loads(open("conf.json").read())
    url = "https://api.openweathermap.org/data/2.5/weather?lat="+ str(coordinates['result']['lat']) + "&lon=" + str(coordinates['result']['lng']) + "&APPID=" + key['OpenWeatherMapAPIKey']
    response = requests.get(url)
    if response.ok:
        endTime = time.time()
        info = {"API": "OpenWeatherMap", "Request": url, "Response": response.status_code, "Latency": (endTime - startTime)}
        writeToLogFile(info)

        info=response.json()
        result = dict()
        result['weather']=info['weather'][0]['description']
        result['temp']=info['main']['temp']
        result['pressure']=info['main']['pressure']
        result['humidity']=info['main']['humidity']
        return {"response": response, "result": result}
    else:
        endTime = time.time()
        info = {"API": "OpenWeatherMap", "Request": url, "Response": response.status_code, "Latency": (endTime - startTime)}
        writeToLogFile(info)
        return False

def getImageofCity(cityName):
    startTime = time.time()
    url = "https://api.teleport.org/api/urban_areas/slug:"+ str(cityName).lower() +"/images/"
    response = requests.get(url)
    if response.ok:
        endTime = time.time()
        info = {"API": "Teleport", "Request": url, "Response": response.status_code, "Latency": (endTime - startTime)}
        writeToLogFile(info)
        return {"response": response, "result": response.json()['photos'][0]['image']['web']}
    else:
        endTime = time.time()
        info = {"API": "Teleport", "Request": url, "Response": "404 Not found.", "Latency": (endTime - startTime)}
        writeToLogFile(info)
        return {"response": response, "result": "Not found"}


class MyServer(HTTPServer):
    pass

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        startTime=time.time()
        # self.path e calea url care a fost rulata
        if self.path.find("metrics") != -1:
            #am gasit metrics in url deci calculam metricile
            logs = json.loads(open("logs.json").read())

            myApiTotal = 0
            myApiCount = 0            
            openCageApiTotal = 0
            openCageApiCount = 0
            openWeatherMapTotal = 0
            openWeatherMapCount = 0
            teleportApiTotal = 0
            teleportApiCount = 0

            successfullCalss = 0

            for log in logs:
                if log['API'] == "My Api":
                    myApiTotal += log['Latency']
                    myApiCount += 1
                if log['API'] == "OpenCageData":
                    openCageApiTotal += log['Latency']
                    openCageApiCount += 1
                if log['API'] == "OpenWeatherMap":
                    openWeatherMapTotal += log['Latency']
                    openWeatherMapCount += 1
                if log['API'] == "Teleport":
                    teleportApiTotal += log['Latency']
                    teleportApiCount += 1
                if log["Response"] == 200:
                    successfullCalss += 1
            
            result = dict()
            result['myApiAverageLatency']=myApiTotal/myApiCount
            result['OpenCageAPIAverageLatency']=openCageApiTotal/openCageApiCount
            result['OpenWeatherMapAPIAverageLatency']=openWeatherMapTotal/openWeatherMapCount
            result['TeleportAPIAverageLatency']=teleportApiTotal/teleportApiCount
            result['SuccessRate']=successfullCalss/len(logs)
            result['logs']=logs

            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        elif self.path.find("api") != -1:
            #am gasit api in url deci facem functionalitatea principala
            #calculam coordonatele orasului si le trimitem in pagina html
            parameter=self.path.split("=")[-1]
            latLong = getLatLongFromCityName(parameter)
            weather = getWeatherFromLatLong(latLong)
            image =getImageofCity(parameter)
            result = dict()
            result['city'] = latLong['result']
            result['weather'] = weather['result']
            result['image'] = image['result']
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            endTime = time.time()
            writeToLogFile({"API": "My Api", "Request": self.path, "Response": 200, "Latency": (endTime - startTime)})
        else:
            #nu se potriveste cu nimic deci ii trimit pagina index.html
            self.send_response(200)
            self.end_headers()
            htmlPage = open("./index.html").read()
            self.wfile.write(htmlPage.encode())
        return

httpd = MyServer(('0.0.0.0', 8000), MyHandler) #Ruleaza la portul 8000 adresa: http://localhost:8000/
httpd.serve_forever()
