from urllib.request import Request
from api_messages import *

import flask
from flask_api import status
from typing import List
import sys

import psycopg2


conn = psycopg2.connect(dbname='persons', user='program',
                        password='test', host='localhost')
app = flask.Flask(__name__)


# DB executors

def getAllPersons() -> List[PersonResponse]:
    with conn.cursor() as cursor:
        cursor.execute('SELECT id, name, age, address, work FROM persons')
        persons_data = [PersonResponse(*e) for e in cursor]
        return persons_data


def getParticularPerson(id: int) -> Union[PersonResponse, None]:
    with conn.cursor() as cursor:
        cursor.execute(
            'SELECT id, name, age, address, work FROM persons WHERE id = %s', (id,))
        person_data = cursor.fetchone()
        if person_data != None:
            return PersonResponse(*person_data)
        else:
            return None


def createPerson(person: PersonRequest) -> int:
    with conn.cursor() as cursor:
        cursor.execute('INSERT INTO persons(id, name, age, address, work)' +
                       'VALUES (DEFAULT, %s, %s, %s, %s)' +
                       'RETURNING id',
                       (person.name, person.age, person.address, person.work))
        conn.commit()
        row = cursor.fetchone()
        return row[0]


def removePerson(id: int):
    with conn.cursor() as cursor:
        cursor.execute('DELETE FROM persons WHERE id = %s', (id,))
        conn.commit()


def patchPerson(id: int, person: PersonRequest) -> Union[PersonResponse, None]:
    params = [person.name]
    if person.age != None:
        params.append(person.age)
    if person.address != None:
        params.append(person.address)
    if person.work != None:
        params.append(person.work)
    params.append(id)

    with conn.cursor() as cursor:
        cursor.execute('UPDATE persons SET name = %s' +
                       (', age = %s' if person.age != None else '') +
                       (', address = %s' if person.address != None else '') +
                       (', work = %s' if person.work != None else '') +
                       'WHERE id = %s',
                       params)
        conn.commit()

    return getParticularPerson(id)


# Parsing

def parseInt32(s: str):
    try:
        val = int(s)
    except:
        return None
    # TODO: validate range
    return val


def parsePersonRequest(request: Request) -> Union[PersonRequest, None]:
    if not request.is_json:
        return None
    if request.json.get("name", None) == None:
        return None
    return PersonRequest(
        name=request.json.get("name"),
        age=request.json.get("age"),
        address=request.json.get("address"),
        work=request.json.get("work"),
    )


# Routes

@app.route('/api/v1/persons/<id>', methods=['GET', 'PATCH', 'DELETE'])
def personRoute(id):
    int_id = parseInt32(id)
    if int_id == None:
        return flask.Response(
            ErrorResponse(msg=f'Wrong id format: `{id}`').toJSON(),
            status.HTTP_404_NOT_FOUND,
        )

    if flask.request.method == 'GET':
        person = getParticularPerson(int_id)
        if person != None:
            return person.toJSON()
        else:
            return flask.Response(
                ErrorResponse(msg=f'There is no person with id {id}').toJSON(),
                status.HTTP_404_NOT_FOUND,
            )

    elif flask.request.method == 'PATCH':
        personRequest = parsePersonRequest(flask.request)
        if personRequest == None:
            errBody = ValidationErrorResponse(
                msg='Error while parsing person request', errors={'x': 'y'}).toJSON()
            return flask.Response(errBody, status.HTTP_400_BAD_REQUEST)

        person = patchPerson(int_id, personRequest)
        if person != None:
            return flask.Response(person.toJSON(), status.HTTP_200_OK)
        else:
            return flask.Response(
                ErrorResponse(msg=f'There is no person with id {id}').toJSON(),
                status.HTTP_404_NOT_FOUND,
            )

    elif flask.request.method == 'DELETE':
        removePerson(int_id)
        return flask.Response('', status.HTTP_204_NO_CONTENT)

    else:
        return flask.Response(
            ErrorResponse(msg='Smth went wrong: unexpected method').toJSON(),
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@app.route('/api/v1/persons', methods=['GET', 'POST'])
def personsRoute():
    if flask.request.method == 'GET':
        persons = getAllPersons()
        return flask.Response(arrToJson(persons))

    elif flask.request.method == 'POST':
        personRequest = parsePersonRequest(flask.request)
        if personRequest == None:
            errBody = ValidationErrorResponse(
                msg='Error while parsing person request', errors={'x': 'y'}).toJSON()
            return flask.Response(errBody, status.HTTP_400_BAD_REQUEST)

        newId = createPerson(personRequest)
        resp = flask.Response('', status.HTTP_201_CREATED)
        resp.headers['Location'] = f'/api/v1/persons/{newId}'
        return resp

    else:
        return flask.Response(
            ErrorResponse(msg='Smth went wrong: unexpected method').toJSON(),
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


port = 8080
if len(sys.argv) > 1:
    port = int(sys.argv[1])

app.run(debug=True, port=port)
