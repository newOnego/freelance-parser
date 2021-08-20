import sqlite3
from config import *

def ensureConnection(func):
	def inner(*args, **kwargs):
		with sqlite3.connect("database.db") as conn:
			kwargs["conn"] = conn
			res = func(*args, **kwargs)
		return res
	return inner

@ensureConnection
def initDB(conn, force: bool = False):
	c = conn.cursor()
	if force:
		c.execute("DROP TABLE IF EXISTS pageInfo")
		c.execute("DROP TABLE IF EXISTS statistics")
	c.execute("""
		CREATE TABLE IF NOT EXISTS pageInfo (
			link            TEXT NOT NULL
		)
	""")
	c.execute("""
		CREATE TABLE IF NOT EXISTS statistics (
			requests        TEXT NOT NULL,
			traffic         TEXT NOT NULL,
			id              TEXT NOT NULL
		)
	""")
	conn.commit()

# Функции для работы с заказами на сайте.
@ensureConnection
def addingInfo(conn, link: str):
	c = conn.cursor()
	c.execute("INSERT INTO pageInfo (link) VALUES (?)", (link, ))
	conn.commit()
@ensureConnection
def verificationInfo(conn):
	c = conn.cursor()
	c.execute("SELECT link FROM pageInfo")
	result = c.fetchone()
	if result:
		return result[0]
@ensureConnection
def deleteInfo(conn):
	c = conn.cursor()
	c.execute("DELETE FROM pageInfo")
	conn.commit()

# Функции для статистики.
@ensureConnection
def addingStatistics(conn, requests: int, traffic: int, id: int):
	c = conn.cursor()
	c.execute("INSERT INTO statistics (requests, traffic, id) VALUES (?, ?, ?)", (requests, traffic, id))
	conn.commit()
@ensureConnection
def verificationRequests(conn):
	c = conn.cursor()
	c.execute("SELECT requests FROM statistics")
	result = c.fetchone()
	if result:
		return result[0]
@ensureConnection
def verificationTraffic(conn):
	c = conn.cursor()
	c.execute("SELECT traffic FROM statistics")
	result = c.fetchone()
	if result:
		return result[0]
@ensureConnection
def updateStatistics(conn, requests: int, traffic: int, id: int):
	c = conn.cursor()
	c.execute("UPDATE statistics SET requests = ?, traffic = ? WHERE id = ?", (requests, traffic, id))
	conn.commit()