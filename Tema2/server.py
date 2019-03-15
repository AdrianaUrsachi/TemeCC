from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
import cgi, json, codecs, requests, time, threading, random
from socketserver import ThreadingMixIn
import uuid

def saveChanges():
    open("owners.json", 'w').write(json.dumps(owners))
    open("brands.json", 'w').write(json.dumps(brands))
    open("gadgets.json", 'w').write(json.dumps(gadgets))

def findOwner(id):
    for owner in owners:
        if str(owner['id']) == str(id):
            return owner
    return False

def findBrand(id):
    for brand in brands:
        if str(brand['id']) == str(id):
            return brand
    return False

def findGadget(id):
    for gadget in gadgets:
        if str(gadget['id']) == str(id):
            return gadget
    return False

def findBrandGadgets(id):
    result = []

    if findBrand(id) == False:
        return False

    for gadget in gadgets:
        if str(gadget['brandId']) == str(id):
            result.append(gadget)

    return result

def findOwnerGadgets(id):
    result = []

    if findOwner(id) == False:
        return False

    for gadget in gadgets:
        if str(gadget['ownerId']) == str(id):
            result.append(gadget)

    return result

def handleOwnersGet(pathRoute):
    code = 200 #OK

    if len(pathRoute) == 1:
        data = owners
        if len(data) == 0:
            code = 204   #No content
        return {'code': code, 'data': data}
    elif len(pathRoute) == 2:
        data = findOwner(pathRoute[1])
        if data != False:
            return {'code': code, 'data': data}
    elif len(pathRoute) == 3:
        data = findOwnerGadgets(pathRoute[1])
        if data != False and len(data) == 0:
            code = 204
        if data != False:
            return {'code': code, 'data': data}
    elif len(pathRoute) == 4:
        data = findOwnerGadgets(pathRoute[1])
        if data == False:
            return {'code': 404, 'data': ''} #Not found
        for d in data:
            if str(d['id']) == str(pathRoute[3]):
                return {'code': code, 'data': d}

    return {'code': 404, 'data': ''}




def handleGadgetsGet(pathRoute):
    code = 200

    if len(pathRoute) == 1:
        data = gadgets
        if len(data) == 0:
            code = 204
        return {'code': code, 'data': data}
    elif len(pathRoute) == 2:
        data = findGadget(pathRoute[1])
        if data != False:
            return {'code': code, 'data': data}
    elif len(pathRoute) == 3 and pathRoute[2] == 'owner':
        data = findGadget(pathRoute[1])
        if data == False:
            return {'code': 404, 'data': ''}
        owner = findOwner(data['ownerId'])
        if owner == False:
            return {'code': 204, 'data': ""}
        else:
            return {'code': code, 'data': owner}
    elif len(pathRoute) == 3 and pathRoute[2] == 'brand':
        data = findGadget(pathRoute[1])
        if data == False:
            return {'code': 404, 'data': ''}
        brand = findBrand(data['brandId'])
        if brand != False:
            return {'code': code, 'data': brand}

    return {'code': 404, 'data': ''}

def handleBrandsGet(pathRoute):
    code = 200

    if len(pathRoute) == 1:
        data = brands
        if len(data) == 0:
            code = 204
        return {'code': code, 'data': data}
    elif len(pathRoute) == 2:
        data = findBrand(pathRoute[1])
        if data != False:
            return {'code': code, 'data': data}
    elif len(pathRoute) == 3:
        data = findBrandGadgets(pathRoute[1])
        if data != False and len(data) == 0:
            code = 204
        if data != False:
            return {'code': code, 'data': data}
    elif len(pathRoute) == 4:
        data = findBrandGadgets(pathRoute[1])
        if data == False:
            return {'code': 404, 'data': ''}
        for d in data:
            if str(d['id']) == str(pathRoute[3]):
                return {'code': code, 'data': d}

    return {'code': 404, 'data': ''}

def handleOwnersPost(pathRoute,inputData):
    code = 201

    if len(pathRoute) == 1:
        try:
            newOwner = {'id': random.getrandbits(100), 'name': inputData['name'], 'age': inputData['age']}
        except:
            return {'code': 400, 'data': ""}
        owners.append(newOwner)
        data = newOwner
        return {'code': code, 'data': data}

def handleGadgetsPost(pathRoute,inputData):
    code = 201  #Created

    if len(pathRoute) == 1:
        try:
            newGadget = {'id': random.getrandbits(100), 'name': inputData['name'], 'brandId': inputData['brandId'], 'ownerId': inputData['ownerId']}
        except:
            return {'code': 400, 'data': ""}  #Bad request
        
        if not findBrand(newGadget['brandId']) or not findOwner(newGadget['ownerId']):
            return {'code': 404, 'data': ""}
        
        gadgets.append(newGadget)
        data = newGadget
        return {'code': code, 'data': data}

def handleBrandsPost(pathRoute,inputData):
    code = 201
    if len(pathRoute) == 1:
        try:
            newBrand = {'id': random.getrandbits(100), 'name': inputData['name']}
        except:
            return {'code': 400, 'data': ""}

        brands.append(newBrand)
        data = newBrand
        return {'code': code, 'data': data}
        

def handleOwnersPut(pathRoute,inputData):
    code = 200
    try:
        updatedOwner = {'id': inputData['id'], 'name': inputData['name'], 'age': inputData['age']}
    except:
        return {'code': 400, 'data': ""}

    for i in range(0, len(owners)):
        if owners[i]['id'] == updatedOwner['id']:
            owners[i] = updatedOwner
            return {'code': code, 'data': updatedOwner}
    return {'code': 404, 'data': ''}

def handleGadgetsPut(pathRoute,inputData):
    code = 200 #OK

    try:
        updatedGadget = {'id': inputData['id'], 'name': inputData['name'], 'ownerId': inputData['ownerId'], 'brandId': inputData['brandId']}
    except:
        return {'code': 400, 'data': ""}

    if not findBrand(updatedGadget['brandId']) or not findOwner(updatedGadget['ownerId']):
            return {'code': 404, 'data': ""}

    for i in range(0, len(gadgets)):
        if gadgets[i]['id'] == updatedGadget['id']:
            gadgets[i] = updatedGadget
            return {'code': code, 'data': updatedGadget}
    return {'code': 404, 'data': ''}

def handleBrandsPut(pathRoute,inputData):
    code = 200
    try:
        updatedBrand = {'id': inputData['id'], 'name': inputData['name']}
    except:
        return {'code': 400, 'data': ""}

    for i in range(0, len(brands)):
        if brands[i]['id'] == updatedBrand['id']:
            brands[i] = updatedBrand
            return {'code': code, 'data': updatedBrand}
    return {'code': 404, 'data': ''}

def handleOwnersDelete(pathRoute):
    code = 204 #No Content

    if len(pathRoute) == 2:
        for i in range(0, len(owners)):
            if str(owners[i]['id']) == str(pathRoute[1]):
                ownerGadgets = findOwnerGadgets(owners[i]['id'])
                for oG in ownerGadgets:
                    deleteGadget(oG['id'])
                owners.pop(i)
                return {'code': code, 'data': ""}

    return {'code': 404, 'data': ""}



def deleteGadget(id):
    for i in range(0,len(gadgets)):
        if str(gadgets[i]['id']) == str(id):
            gadgets.pop(i)
            return True
    return False 

def handleGadgetsDelete(pathRoute):
    code = 204

    if len(pathRoute) == 2:
        if deleteGadget(pathRoute[1]):
            return {'code': code, 'data': ""}
    return {'code': 404, 'data': ""}

def handleBrandsDelete(pathRoute):
    code = 204

    if len(pathRoute) == 2:
        for i in range(0, len(brands)):
            if str(brands[i]['id']) == str(pathRoute[1]):
                brandGadgets = findBrandGadgets(brands[i]['id'])
                for bG in brandGadgets:
                    deleteGadget(bG['id'])
                brands.pop(i)
                return {'code': code, 'data': ""}
                
    return {'code': 404, 'data': ""}


class RestHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pathRoute = self.path.split('/')[1:]

        result = {'code': 400, 'data':''}

        try:
            if pathRoute[0] == 'owners':
                result = handleOwnersGet(pathRoute)
            elif pathRoute[0] == 'gadgets':
                result = handleGadgetsGet(pathRoute)
            elif pathRoute[0] == 'brands':
                result = handleBrandsGet(pathRoute)

            self.send_response(result['code'])
            self.end_headers()
            if result['data'] != '':
                self.wfile.write(json.dumps(result['data']).encode())
        except:
            self.send_response(500) #Internal Server Error
            self.end_headers()
            return

    def do_POST(self):
        inputData = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        pathRoute = self.path.split('/')[1:]

        result = {'code': 400, 'data':''}

        if self.headers['Content-Type'] != 'application/json':
            self.send_response(415) #Unsupported Media Type
            self.end_headers()
            return
        try:      
            if pathRoute[0] == 'owners':
                result = handleOwnersPost(pathRoute, inputData)
            elif pathRoute[0] == 'gadgets':
                result = handleGadgetsPost(pathRoute, inputData)
            elif pathRoute[0] == 'brands':
                result = handleBrandsPost(pathRoute, inputData)

            self.send_response(result['code'])
            self.end_headers()
            if result['data'] != '':
                self.wfile.write(json.dumps(result['data']).encode())
            saveChanges()
            #print("DADA")
            return
        except:
            self.send_response(500)
            self.end_headers()
            return

    def do_PUT(self):
        pathRoute = self.path.split('/')[1:]

        result = {'code': 400, 'data':''}

        if self.headers['Content-Type'] != 'application/json':
            self.send_response(415)
            self.end_headers()
            return
        try:
            inputData = json.loads(self.rfile.read(int(self.headers['Content-Length'])))

            if pathRoute[0] == 'owners':
                result = handleOwnersPut(pathRoute,inputData)
            elif pathRoute[0] == 'gadgets':
                result = handleGadgetsPut(pathRoute,inputData)
            elif pathRoute[0] == 'brands':
                result = handleBrandsPut(pathRoute,inputData)

            self.send_response(result['code'])
            self.end_headers()
            if result['data'] != '':
                self.wfile.write(json.dumps(result['data']).encode())
            saveChanges()
        except:
            self.send_response(500)
            self.end_headers()
            return

    def do_DELETE(self):
        pathRoute = self.path.split('/')[1:]

        result = {'code': 400, 'data':''}

        try:
            if pathRoute[0] == 'owners':
                result = handleOwnersDelete(pathRoute)
            elif pathRoute[0] == 'gadgets':
                result = handleGadgetsDelete(pathRoute)
            elif pathRoute[0] == 'brands':
                result = handleBrandsDelete(pathRoute)

            self.send_response(result['code'])
            self.end_headers()
            if result['data'] != '':
                self.wfile.write(json.dumps(result['data']).encode())
            saveChanges()
        except:
            self.send_response(500)
            self.end_headers()
            return
        



class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

gadgets = json.loads(open("gadgets.json").read())
brands = json.loads(open("brands.json").read())
owners = json.loads(open("owners.json").read())

httpd = ThreadedHTTPServer(('0.0.0.0', 8000), RestHTTPRequestHandler)
httpd.serve_forever()