import sqlite3
from typing import Dict
from fastapi import FastAPI, HTTPException, Response, Depends, status, Request
from pydantic import BaseModel
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from hashlib import sha256
from starlette.responses import RedirectResponse
from fastapi import FastAPI

app = FastAPI()

class AlbumRq(BaseModel):
	title: str
	artist_id: int
class AlbumResp(BaseModel):
	AlbumId: int
	Title: str
	ArtistId: int

class Customer(BaseModel):
	company: str = None
	address: str = None
	city: str = None
	state: str = None
	country: str = None
	postalcode: str = None
	fax: str = None

class AlbumResp(BaseModel):
	CustomerId: int
	FirstName: str
	LastName: str
	Company: str
	Address: str
	City: str
	State: str
	Country: str
	PostalCode: str
	Phone: str
	Fax: str
	Email: str
	SupportRepId: int

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

@app.post("/albums")
async def read_albums(response: Response, rq: AlbumRq):
	app.db_connection.row_factory = sqlite3.Row
	artists = app.db_connection.execute(
		"SELECT ArtistId FROM artists WHERE Artistid = ?",
		(rq.artist_id, )).fetchone()
	if not artists:
		response.status_code = status.HTTP_404_NOT_FOUND
		return {"detail":{"error":"Artist with this ID does not exist."}}
	else:
		cursor = app.db_connection.execute(
		"INSERT INTO albums (Title, ArtistId) VALUES (?, ?)", (rq.title, rq.artist_id, ))
		app.db_connection.commit()
		new_album_id = cursor.lastrowid
		app.db_connection.row_factory = sqlite3.Row
		album = app.db_connection.execute("SELECT * FROM albums WHERE AlbumId = ?", (new_album_id,)).fetchone()
		response.status_code = status.HTTP_201_CREATED
		return album

@app.get("/albums/{album_id}")
async def read_albums(response: Response, album_id: int):
	app.db_connection.row_factory = sqlite3.Row
	cursor =  app.db_connection.execute("SELECT * FROM albums WHERE AlbumId = ?",
		(album_id, ))
	album = cursor.fetchone()
	if album is None:
		response.status_code = status.HTTP_404_NOT_FOUND
		return {"detail":{"error":"Album with that ID does not exist."}}
	return album

@app.put("/customers/{customer_id}")
async def read_customers(response: Response, customer_id: int, customer: Customer):
	if_customer = app.db_connection.execute("SELECT CustomerId FROM customers WHERE CustomerId = ?",
										(customer_id,)).fetchone()
	if not if_customer:
		response.status_code = status.HTTP_404_NOT_FOUND
		return {"detail":{"error":"Artist with this ID does not exist."}}
	if customer.company:
		cursor = app.db_connection.execute("UPDATE customers SET company = ? WHERE CustomerId = ?",
									   (customer.company, customer_id))
	if customer.address:
		cursor = app.db_connection.execute("UPDATE customers SET address = ? WHERE CustomerId = ?",
									   (customer.address, customer_id))
	if customer.city:
		cursor = app.db_connection.execute("UPDATE customers SET city = ? WHERE CustomerId = ?",
									   (customer.city, customer_id))
	if customer.state:
		cursor = app.db_connection.execute("UPDATE customers SET state = ? WHERE CustomerId = ?",
									   (customer.state, customer_id))
	if customer.country:
		cursor = app.db_connection.execute("UPDATE customers SET country = ? WHERE CustomerId = ?",
									   (customer.country, customer_id))
	if customer.postalcode:
		cursor = app.db_connection.execute("UPDATE customers SET postalcode = ? WHERE CustomerId = ?",
									   (customer.postalcode, customer_id))
	if customer.fax:
		cursor = app.db_connection.execute("UPDATE customers SET fax = ? WHERE CustomerId = ?",
								   (customer.fax, customer_id))
	app.db_connection.commit()
	app.db_connection.row_factory = sqlite3.Row
	updated_customer = app.db_connection.execute("SELECT * FROM customers WHERE CustomerId = ?", (customer_id,)).fetchone()
	return updated_customer



'''


@app.post("/patient")
def add_patient(response: Response, rq: PatientRq, session_token: str = Depends(check_cookie)):
	if session_token is None:
		response.status_code = status.HTTP_401_UNAUTHORIZED
		return MESSAGE_UNAUTHORIZED
	pid=f"id_{app.next_patient_id}"
	app.patients[pid]=rq.dict()
	response.status_code = status.HTTP_302_FOUND
	response.headers["Location"] = f"/patient/{pid}"
	app.next_patient_id+=1




'''

















