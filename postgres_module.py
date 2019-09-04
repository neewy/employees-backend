from injector import Module, Injector, inject, singleton
from flask import Flask, Request, jsonify
from flask_injector import FlaskInjector
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import Column, String

# We use standard SQLAlchemy models rather than the Flask-SQLAlchemy magic, as
# it requires a global Flask app object and SQLAlchemy db object.
Base = declarative_base()

class KeyValue(Base):
    __tablename__ = 'data'

    key = Column(String, primary_key=True)
    value = Column(String)

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def serializable(self):
        return

class PostgresModule(Module):
    def __init__(self, app):
        self.app = app

    """Configure the application."""

    def configure(self, binder):
        # We configure the DB here, explicitly, as Flask-SQLAlchemy requires
        # the DB to be configured before request handlers are called.
        db = self.configure_db(self.app)
        binder.bind(SQLAlchemy, to=db, scope=singleton)

    def configure_db(self, app):
        db = SQLAlchemy(app)
        Base.metadata.create_all(db.engine)
        db.session.add_all([KeyValue('hello', 'world'), KeyValue('goodbye', 'cruel world')])
        db.session.commit()
        return db