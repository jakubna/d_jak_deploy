from typing import Dict
import secrets
from fastapi import FastAPI, HTTPException, Response, Cookie, Depends, status
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from hashlib import sha256
from starlette.responses import RedirectResponse



app = FastAPI()
security = HTTPBasic()

app.counter = -1
app.database = {}

app.secret_key = "very constatn and random secret, best 64 characters"
app.users = {"trudnY": "PaC13Nt", "admin": "admin"}
app.sessions={}
app.message_unauthorized = "Log in to access this page."
app.secret = "secret"
app.tokens = []



@app.get("/")
def root():
	return "hello"

class GivePostMethodResp(BaseModel):
	method: str

class GiveMeSomethingRq(BaseModel):
	name: str
	surename: str


class GiveMeSomethingResp(BaseModel):
	id: int
	patient: Dict

@app.get("/welcome")
def welcome():
	return "hi"


def login_check_cred(credentials: HTTPBasicCredentials = Depends(security)):
	correct_username = secrets.compare_digest(credentials.username, "admin")
	correct_password = secrets.compare_digest(credentials.password, "admin")
	if not (correct_username and correct_password):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Incorrect email or password",
			headers={"WWW-Authenticate": "Basic"},
		)
	session_token = sha256(bytes(f"{credentials.username}{credentials.password}{app.secret_key}", encoding='utf8')).hexdigest()
	app.sessions[session_token]=credentials.username
	return session_token

@app.post("/login")
def login(response: Response, session_token: str = Depends(login_check_cred)):
	response.headers["Location"] = "/welcome"
	response.set_cookie(key="session_token", value=session_token)




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
		raise HTTPException(status_code=204, detail="no_content")
	return app.database[pk]