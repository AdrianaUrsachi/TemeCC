import requests, threading, time, random

def makeRequest(cityName):
    startTime = time.time()
    url = "http://localhost:8000/api/city=" + cityName
    response = requests.get(url)

cities = ["Bucharest","London","Iasi","Madrid","Lisbon","New York"]

for i in range(0,10):
    threads = []
    for j in range(0,5):
        city = random.choice(cities)
        t = threading.Thread(target=makeRequest, args=(city,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()