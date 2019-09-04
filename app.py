import os
from injector import Module, Injector, inject, singleton
from postgres_module import PostgresModule, KeyValue
from flask import Flask, Request
from flask_jsonpify import jsonify
from flask_cors import CORS, cross_origin
from flask_restful import Resource, Api
from json import dumps
from flask_injector import FlaskInjector
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import Column, String

def configure_views(app):
    @app.route('/<key>')
    def get(key, db: SQLAlchemy):
        try:
            kv = db.session.query(KeyValue).filter(KeyValue.key == key).one()
        except NoResultFound:
            response = jsonify(status='No such key', context=key)
            response.status = '404 Not Found'
            return response
        return jsonify(key=kv.key, value=kv.value)

    @app.route('/')
    def list(db: SQLAlchemy):
        data = [i.key for i in db.session.query(KeyValue).order_by(KeyValue.key)]
        return jsonify(keys=data)

    @app.route('/', methods=['POST'])
    def create(request: Request, db: SQLAlchemy):
        kv = KeyValue(request.form['key'], request.form['value'])
        db.session.add(kv)
        db.session.commit()
        response = jsonify(status='OK')
        response.status = '201 CREATED'
        return response

    @app.route('/<key>', methods=['DELETE'])
    def delete(db: SQLAlchemy, key):
        db.session.query(KeyValue).filter(KeyValue.key == key).delete()
        db.session.commit()
        response = jsonify(status='OK')
        response.status = '200 OK'
        return response     

# Initialize Flask-Injector. This needs to be run *after* you attached all
# views, handlers, context processors and template globals.

def main():
    app = Flask(__name__)
    api = Api(app)
    CORS(app)

    app.config.from_object(os.environ['APP_SETTINGS'])
    print(os.environ['APP_SETTINGS'])
    app.config.update(DB_CONNECTION_STRING=':memory:', SQLALCHEMY_DATABASE_URI='sqlite://')
    app.debug = True

    injector = Injector([PostgresModule(app)])
    configure_views(app=app)

    FlaskInjector(app=app, injector=injector)

    client = app.test_client()

    response = client.get('/')
    print('%s\n%s%s' % (response.status, response.headers, response.data))
    response = client.post('/', data={'key': 'foo', 'value': 'bar'})
    print('%s\n%s%s' % (response.status, response.headers, response.data))
    response = client.get('/')
    print('%s\n%s%s' % (response.status, response.headers, response.data))
    response = client.get('/hello')
    print('%s\n%s%s' % (response.status, response.headers, response.data))
    response = client.delete('/hello')
    print('%s\n%s%s' % (response.status, response.headers, response.data))
    response = client.get('/')
    print('%s\n%s%s' % (response.status, response.headers, response.data))
    response = client.get('/hello')
    print('%s\n%s%s' % (response.status, response.headers, response.data))
    response = client.delete('/hello')
    print('%s\n%s%s' % (response.status, response.headers, response.data))


if __name__ == '__main__':
    main()