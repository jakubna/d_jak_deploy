import sqlite3
from typing import Dict
from fastapi import FastAPI, HTTPException, Response, Depends, status, Request
from pydantic import BaseModel
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from hashlib import sha256
from starlette.responses import RedirectResponse
from fastapi import FastAPI

app = FastAPI()

@app.on_event("startup")
async def startup():
	app.db_connection = sqlite3.connect('chinook.db')


@app.on_event("shutdown")
async def shutdown():
	app.db_connection.close()


@app.get("/data")
async def root():
	cursor = app.db_connection.execute("SELECT name FROM tracks")
	data = cursor.fetchall()
	return {"data": data}

@app.get("/tracks")
async def read_tracks(page: int = 0, per_page: int = 10):
	app.db_connection.row_factory = sqlite3.Row
	data = app.db_connection.execute(
		"SELECT * FROM tracks ORDER BY TrackId LIMIT :per_page OFFSET :per_page*:page",
		{'page': page, 'per_page': per_page}).fetchall()

	return data

@app.get("/tracks/composers")
async def read_tracks(response: Response, composer_name: str = 'Angus Young, Malcolm Young, Brian Johnson'):
	app.db_connection.row_factory = sqlite3.Row
	tracks = app.db_connection.execute(
		"SELECT Name FROM tracks WHERE Composer = ? ORDER BY Name",
		(composer_name, )).fetchall()
	if len(tracks) == 0:
		response.status_code = status.HTTP_404_NOT_FOUND
		return {"detail":{"error":"Can't find any songs of that composer."}}
	else:	
		data = [x['Name'] for x in tracks]
		return data


'''


@app.get("/patient/{pk}")
async def read_item(pk: int, response: Response, session_token: str = Depends(check_cookie)):
	if session_token is None:
		response.status_code = status.HTTP_401_UNAUTHORIZED
		return app.message_unauthorized
	if pk not in app.database:
		raise HTTPException(status_code=204, detail="no_content")
	return app.database[pk]




'''

















