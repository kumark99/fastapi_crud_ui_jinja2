__author__="Kumar Krishnan"

#imports
from pydantic import BaseModel
from fastapi import FastAPI, Request, Response,status
from pymongo import MongoClient
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Form, Cookie, Depends
from starlette.responses import RedirectResponse, Response
import datetime,time

#MongoDB Connection info
client = MongoClient("mongodb://localhost:27017/")
#Database
pets_db = client['pets_db']
#Collection
fish_collection = pets_db['fish']

#Model
class Fish(BaseModel):
    fish_id: int
    fish_name: str
    fish_image:str
    fish_description:str

#Initialize
app = FastAPI()

#Static file serv
app.mount("/static", StaticFiles(directory="static"), name="static")
#Jinja2 Template directory
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/fish/{id}", response_class=HTMLResponse)
async def read_fish(request: Request, id: int):
    print('find fish called with id :'+str(id))
    result = fish_collection.find_one({'fish_id': id})
    print(result['fish_name'])
    return templates.TemplateResponse("view_fish.html", {"request": request, "fish": result})

@app.get("/fish", response_class=HTMLResponse)
async def read_all_fish(request: Request):
    result = fish_collection.find({})
    print(result)
    return templates.TemplateResponse("list_fish.html", {"request": request, "fish_list": result})

@app.get("/createui", response_class=HTMLResponse)
async def create_fish_ui(request: Request):
    return templates.TemplateResponse("new_fish.html", {"request": request})


@app.post("/create",response_class=HTMLResponse)
async def create_fish(request:Request,fishId:str = Form(...),fishName:str = Form(...),fishImage:str = Form(...),fishDescription:str = Form(...)):
    print('fish_id :'+str(fishId) +', fish_name:'+str(fishName)+', fishimage:'+str(fishImage)+', fisdescription:'+str(fishDescription))
    #initialize the model
    fish = Fish(fish_id=fishId,fish_name=fishName,fish_image=fishImage,fish_description=fishDescription)
    print(str(fish.dict()))
    id = fish_collection.insert_one(fish.dict()).inserted_id
    print(" Fish added : now db size " + str(id))
    time.sleep(1)
    result = fish_collection.find({})
    return templates.TemplateResponse("list_fish.html", {"request": request, "fish_list": result})


@app.get("/fish/delete/{id}",response_class=HTMLResponse)
async def delete_fish(id:int,response:Response,request:Request):
    print(" delete fish method called :"+str(id))
    result = fish_collection.delete_one({'fish_id':id})
    time.sleep(1)
    result = fish_collection.find({})
    print(result)
    return templates.TemplateResponse("list_fish.html", {"request": request, "fish_list": result})

@app.get("/fish/edit/{id}",response_class=HTMLResponse)
async def edit_fish(id:int,response:Response,request:Request):
    print(" method called :"+str(id))
    result = fish_collection.find_one({'fish_id':id})
    return templates.TemplateResponse("edit_fish.html", {"request": request, "fish": result})

@app.post("/update",response_class=HTMLResponse)
async def update_fish(request:Request,response:Response,fishId:str = Form(...),fishName:str = Form(...),fishImage:str = Form(...),fishDescription:str = Form(...)):
    print('fish_id :'+str(fishId))
    print('fishname '+str(fishName))
    print('fishimage ' + str(fishImage))
    print('fishdescription ' + str(fishDescription))
    #initialize the model
    fish = Fish(fish_id=fishId,fish_name=fishName,fish_image=fishImage,fish_description=str(fishDescription))
    print(str(fish.dict()))
    #call internal api
    update_api(fish)
    time.sleep(1)
    #get the updated list
    result = fish_collection.find({})
    print(str(result))
    return templates.TemplateResponse("list_fish.html", {"request": request, "fish_list": result})


@app.put("/updateapi",status_code=202)
async def update_api(fish:Fish):
    print('Update api called....'+str(fish.fish_name))
    result = fish_collection.update_one({'fish_id':fish.fish_id},{"$set" : {'fish_name':fish.fish_name}})
    return "UPDATE SUCCESS"

