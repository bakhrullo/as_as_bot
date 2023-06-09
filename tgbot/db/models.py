import datetime

from sqlalchemy import Column, VARCHAR, INTEGER, DateTime, BigInteger, sql

from tgbot.db.database import db


class User(db.Model):
    __tablename__ = 'users'
    query: sql.Select

    id = Column(INTEGER(), primary_key=True, autoincrement=True)
    tg_id = Column(BigInteger(), unique=True)
    lang = Column(VARCHAR(2))
    name = Column(VARCHAR(200))
    number = Column(VARCHAR(20))
    type = Column(VARCHAR(100))
    status = Column(VARCHAR(50))
    region = Column(VARCHAR(50))
    street = Column(VARCHAR(200))
    product = Column(VARCHAR(100))
    date = Column(DateTime, default=datetime.datetime.utcnow())


class Quarter(db.Model):
    __tablename__ = 'quarters'
    query: sql.Select

    id = Column(INTEGER(), primary_key=True, autoincrement=True)
    name = Column(VARCHAR(200))
    city = Column(VARCHAR(200))
    date = Column(DateTime, default=datetime.datetime.utcnow())


class City(db.Model):
    __tablename__ = 'citys'
    query: sql.Select

    id = Column(INTEGER(), primary_key=True, autoincrement=True)
    name_uz = Column(VARCHAR(200))
    name_ru = Column(VARCHAR(200))
    name_en = Column(VARCHAR(200))
    date = Column(DateTime, default=datetime.datetime.utcnow())


class Market(db.Model):
    __tablename__ = 'markets'
    query: sql.Select

    id = Column(INTEGER(), primary_key=True, autoincrement=True)
    name_uz = Column(VARCHAR(200))
    name_ru = Column(VARCHAR(200))
    name_en = Column(VARCHAR(200))
    region = Column(VARCHAR(100))
    address = Column(VARCHAR(200))
    type = Column(VARCHAR(500))
    activity = Column(VARCHAR(500))
    number = Column(VARCHAR(30))
    date = Column(DateTime, default=datetime.datetime.utcnow())



