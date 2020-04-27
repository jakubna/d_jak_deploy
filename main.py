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

def login_check_cred(credentials: HTTPBasicCredentials = Depends(security)):
	correct_username = secrets.compare_digest(credentials.username, "trudnY")
	correct_password = secrets.compare_digest(credentials.password, "PaC13Nt")
	if not (correct_username and correct_password):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Incorrect email or password",
			headers={"WWW-Authenticate": "Basic"},
		)
	session_token = sha256(bytes(f"{credentials.username}{credentials.password}{app.secret_key}", encoding='utf8')).hexdigest()
	app.sessions[session_token]=credentials.username
	return session_token

def check_cookie(session_token: str = Cookie(None)):
	if session_token not in app.sessions:
		session_token = None
	return session_token

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
def welcome(response: Response, session_token: str = Depends(check_cookie)):
	if session_token is None:
		response.status_code = status.HTTP_401_UNAUTHORIZED
		return app.message_unauthorized
	return "hi"




@app.post("/login")
def login(response: Response, session_token: str = Depends(login_check_cred)):
	response.status_code = status.HTTP_302_FOUND
	response.headers["Location"] = "/welcome"
	response.set_cookie(key="session_token", value=session_token)

@app.post("/logout")
def logout(response: Response, session_token: str = Depends(check_cookie)):
	if session_token is None:
		response.status_code = status.HTTP_401_UNAUTHORIZED
		return app.message_unauthorized
	response.status_code = status.HTTP_302_FOUND
	response.headers["Location"] = "/"
	app.sessions.pop(session_token)






@app.get("/method")
def method_get(response: Response, session_token: str = Depends(check_cookie)):
	if session_token is None:
		response.status_code = status.HTTP_401_UNAUTHORIZED
		return app.message_unauthorized
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
def receive_something(rq: GiveMeSomethingRq, response: Response, session_token: str = Depends(check_cookie)):
	if session_token is None:
		response.status_code = status.HTTP_401_UNAUTHORIZED
		return app.message_unauthorized
	app.counter += 1
	app.database[app.counter] = rq.dict()
	return GiveMeSomethingResp(id=app.counter, patient=rq.dict())

@app.get("/patient/{pk}")
async def read_item(pk: int, response: Response, session_token: str = Depends(check_cookie)):
	if session_token is None:
		response.status_code = status.HTTP_401_UNAUTHORIZED
		return app.message_unauthorized
	if pk not in app.database:
		raise HTTPException(status_code=204, detail="no_content")
	return app.database[pk]