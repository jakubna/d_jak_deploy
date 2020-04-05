from typing import Dict

from fastapi import FastAPI, HTTPException

from pydantic import BaseModel


app = FastAPI()

app.counter = 0
app.database = {}

@app.get("/")
def root():
	return {"message": "Hello World during the coronavirus pandemic!"}

class GivePostMethodResp(BaseModel):
	method: str

class GiveMeSomethingRq(BaseModel):
	name: str
	surname: str


class GiveMeSomethingResp(BaseModel):
	id: int
	patient: Dict

@app.get("/method")
def method_get():
	return {"method": "GET"}

@app.put("/method")
def method_put():
	return {"method": "PUT"}

@app.delete("/method")
def method_delete():
	return {"method": "DELETE"}

@app.post("/method", response_model=GivePostMethodResp)
def method_post():
	return GivePostMethodResp(method="POST")

@app.post("/patient", response_model=GiveMeSomethingResp)
def receive_something(rq: GiveMeSomethingRq):
	app.counter += 1
	app.database[app.counter] = rq.dict()
	return GiveMeSomethingResp(id=app.counter, patient=rq.dict())

@app.get("/patient/{pk}")
async def read_item(pk: int):
    if pk not in app.database:
        raise HTTPException(status_code=404, detail="Patient not found")
    return app.database[pk]