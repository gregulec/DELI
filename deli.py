import tornado.ioloop
import tornado.web
from   tornado.options import define, options
import asyncio
import json

define("port", default=8888, help="run on the given port", type=int)
url = "http://localhost:8888/"
cars = []
cid = 0
workers = []
wid = 0
allocations = []
aid = 0

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_status(200)
        self.write("Przydzielanie aut pracownikom")

class CarsHandler(tornado.web.RequestHandler):
    def get(self):
        start = int(self.get_argument("start","0"))
        stop = start + 10
        while (start < stop) & (start < len(cars)):
            self.write(json.dumps(cars[int(start)], ensure_ascii=False))
            start=int(start)+1
        self.set_status(200)
    def post(self):
        global cid
        car_uri = "cars/" + str(cid)
        new_car = {
            "id": cid,
            "brand":"",
            "model":"",
            "number":"",
            "ETag": 0
            }
        cars.append(new_car)
        self.set_status(201)
        self.set_header("Location", url + car_uri)
        self.set_header("ETag", new_car["ETag"])
        self.write('Added new car')
        # self.put
        cid = cid + 1
        
class CarHandler(tornado.web.RequestHandler):
    def get(self, id):
        self.write(json.dumps(cars[int(id)], ensure_ascii=False))
        self.set_status(200)
    def put(self, id):
        if self.request.headers["Content-Type"] == 'application/json':
            data = json.loads(self.request.body.decode("utf-8"))
            if self.request.headers.get("If-Match") != None:
                for i in range(len(cars)):
                    if cars[i]['id'] == int(id):
                        if self.request.headers["If-Match"] == str(cars[i]['ETag']):
                            new_ETag = cars[i]['ETag'] + 1 #wyliczanie nowego ETag przed aktualizacją w przypadku jaky ktość chciał JSONem zmienić ETag
                            cars[i] = data
                            cars[i]['ETag']=new_ETag
                            self.set_status(200)
                            self.set_header("etag", new_ETag)
                            self.write(json.dumps(cars[i], ensure_ascii=False))
                            self.write('Updated car')
                        else:
                            self.set_status(412)
                            self.write('Bad ETag')
            else:
                self.set_status(428)
                self.write('Use If-Match in header')
        else:
            self.set_status(400)
            self.write('Use JSON')
    def delete(self, id):
        global cars
        cars = [car for car in cars if car['id'] is not int(id)]
        self.set_status(204)
        self.finish()

class WorkersHandler(tornado.web.RequestHandler):
    def get(self):
        start = int(self.get_argument("start","0"))
        stop = start + 10
        while (start < stop) & (start < len(workers)):
            self.write(json.dumps(workers[int(start)], ensure_ascii=False))
            start=int(start)+1
        self.set_status(200)
    def post(self):
        global wid
        worker_uri = "workers/" + str(wid)
        new_worker = {
            "id": wid,
            "name":"",
            "lastname":"",
            "age": 0,
            "ETag": 0
            }
        workers.append(new_worker)
        self.set_status(201)
        self.set_header("Location", url+ worker_uri)
        self.set_header("ETag", new_worker["ETag"])
        self.write('Added new worker')
        wid = wid + 1
        
class WorkerHandler(tornado.web.RequestHandler):
    def get(self, id):
        self.write(json.dumps(workers[int(id)], ensure_ascii=False))
        self.set_status(200)
    def put(self, id):
        if self.request.headers["Content-Type"] == 'application/json':
            data = json.loads(self.request.body.decode("utf-8"))    
            if self.request.headers.get("If-Match") != None:
                for i in range(len(workers)):
                    if workers[i]['id'] == int(id):
                        if self.request.headers["If-Match"] == str(workers[i]["ETag"]):
                            new_ETag = workers[i]["ETag"] + 1 #wyliczanie nowego ETag przed aktualizacją w przypadku jaky ktość chciał JSONem zmienić ETag
                            workers[i] = data
                            workers[i]["ETag"]=new_ETag
                            self.set_status(200)
                            self.set_header("etag", new_ETag)
                            self.write(json.dumps(workers[i], ensure_ascii=False))
                            self.write('Updated worker')
                        else:
                            self.set_status(412)
                            self.write('Bad ETag')
            else:
                self.set_status(428)
                self.write('Use If-Match in header')
        else:
            self.set_status(400)
            self.write('Use JSON')
    def delete(self, id):
        global workers
        workers = [worker for worker in workers if worker['id'] is not int(id)]
        self.set_status(204)
        self.finish()
        
class AllocationsHandler(tornado.web.RequestHandler):
    def get(self):
        start = int(self.get_argument("start","0"))
        stop = start + 10
        while (start < stop) & (start < len(allocations)):
            self.write(json.dumps(allocations[int(start)], ensure_ascii=False))
            start=int(start)+1
        self.set_status(200)
    def post(self):
        global aid
        allocation_uri = "allocations/" + str(aid)
        new_alloation = {
            "id": aid,
            "cid":0,
            "wid":0,
            "ETag": 0
            }
        allocations.append(new_alloation)
        self.set_status(201)
        self.set_header("Location", url+ allocation_uri)
        self.set_header("ETag", new_alloation["ETag"])
        self.write('Added new allocation')
        aid = aid + 1
        
class AllocationHandler(tornado.web.RequestHandler):
    def get(self, id):
        self.write(json.dumps(allocations[int(id)], ensure_ascii=False))
        self.set_status(200)
    def put(self, id):
        if self.request.headers["Content-Type"] == 'application/json':
            data = json.loads(self.request.body.decode("utf-8"))
            existCar = [car for car in cars if car['id'] is int(data['cid'])]
            existWorker = [worker for worker in workers if worker['id'] is int(data['wid'])]
            if (existCar != []) & (existWorker != []):
                if self.request.headers.get("If-Match") != None:
                    for i in range(len(allocations)):
                        if allocations[i]['id'] == int(id):
                            if self.request.headers["If-Match"] == str(allocations[i]["ETag"]):
                                new_ETag = allocations[i]["ETag"] + 1 #wyliczanie nowego ETag przed aktualizacją w przypadku jaky ktość chciał JSONem zmienić ETag
                                allocations[i] = data
                                allocations[i]["ETag"]=new_ETag
                                self.set_status(200)
                                self.set_header("etag", new_ETag)
                                self.write(json.dumps(allocations[i], ensure_ascii=False))
                                self.write('Updated allocation')
                            else:
                                self.set_status(412)
                                self.write('Bad ETag')
                else:
                    self.set_status(428)
                    self.write('Use If-Match in header')
            else:
                self.set_status(400)
                self.write('Car or worker do not exist')
        else:
            self.set_status(400)
            self.write('Use JSON')
    def delete(self, id):
        global allocations
        allocations = [allocation for allocation in allocations if allocation['id'] is not int(id)]
        self.set_status(204)
        self.finish()

class TransfersHandler(tornado.web.RequestHandler):
    def post(self):
        if self.request.headers["Content-Type"] == 'application/json':
            global allocations
            global aid
            data = json.loads(self.request.body.decode("utf-8"))    
            fromWorker = int(data["widfrom"])
            toWorker = int(data["widto"])
            existWorker = [worker for worker in workers if worker['id'] is toWorker]
            if existWorker != []:
                for allocation in allocations:
                    if allocation['wid'] == fromWorker:
                        new_alloation = {
                        "id": aid,
                        "cid":allocation['cid'],
                        "wid":toWorker,
                        "ETag": 0
                        }
                        aid = aid + 1
                        allocations.append(new_alloation)
                allocations = [allocation for allocation in allocations if allocation['wid'] is not fromWorker]
                self.set_status(201)
                self.write('Added new allocations')
            else:
                self.set_status(400)
                self.write('Worker not exist')
        else:
            self.set_status(400)
            self.write('Use JSON')

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    tornado.options.parse_command_line()
    tornado.web.Application(debug= True,autoreload=True)
    application = tornado.web.Application([
        ("/", MainHandler), 
        ("/cars", CarsHandler),
        ("/cars/([0-9]+)", CarHandler),
        ("/workers", WorkersHandler),
        ("/workers/([0-9]+)", WorkerHandler),
        ("/allocations", AllocationsHandler),
        ("/allocations/([0-9]+)", AllocationHandler),
        ("/transfers", TransfersHandler)
    ])
    application.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()