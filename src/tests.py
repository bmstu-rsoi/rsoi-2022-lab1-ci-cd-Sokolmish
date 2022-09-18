from api_messages import *
import requests

HOST_PORT = 5000
HOST_ADDRESS = 'localhost'

HOST_URL = f'http://{HOST_ADDRESS}:{HOST_PORT}/api/v1'

TEST_USERNAME = '___TEST_NAME___'
TEST_AGE = 18
TEST_AGE2 = 22
TEST_WORK = 'Rostelecom'


class TestFault(Exception):
    def __init__(self, fault_msg: str, *args: object) -> None:
        super().__init__(*args)
        self.fault_msg = fault_msg


def do_request(addr, method, exp_status, data=None):
    headers = {'Content-Type': 'application/json'}
    if method == 'GET':
        r = requests.get(addr, data, headers=headers)
    elif method == 'POST':
        r = requests.post(addr, data, headers=headers)
    elif method == 'PATCH':
        r = requests.patch(addr, data, headers=headers)
    elif method == 'DELETE':
        r = requests.delete(addr)
    else:
        raise Exception(f'Unsopported method {method}')

    if r.status_code != exp_status:
        raise TestFault(
            f'Status code for `{addr}` {method} request is not NULL')

    if len(r.content) == 0:
        return '', r.headers
    try:
        body = r.json()
    except:
        raise TestFault(
            f'Response for `{addr}` {method} request is not in json format')

    return body, r.headers


def deleteTestUser() -> None:
    body, _ = do_request(f'{HOST_URL}/persons', 'GET', 200)
    if TEST_USERNAME in (x.get('name') for x in body):
        unluckyPerson = next(x for x in body if x.get('name') == TEST_USERNAME)
        unluckyId = int(unluckyPerson.get('id'))
        do_request(f'{HOST_URL}/persons/{unluckyId}', 'DELETE', 204)

        body, _ = do_request(f'{HOST_URL}/persons', 'GET', 200)
        if TEST_USERNAME in (x.get('name') for x in body):
            raise TestFault('Database contains reserved user name')


def createTestUser() -> int:
    newPers = PersonRequest(TEST_USERNAME, age=TEST_AGE,
                            work=TEST_WORK, address=None)
    _, headers = do_request(
        f'{HOST_URL}/persons', 'POST', 201, newPers.toJSON())

    loc_s = headers.get('Location')
    locPrefix = '/api/v1/persons/'
    if loc_s == None:
        raise TestFault(
            'Response for `persons` POST request has no `Location` header')
    if not loc_s.startswith(locPrefix):
        raise TestFault(
            'Response for `persons` POST request has `Location` header in wrong format')
    try:
        loc = int(loc_s[len(locPrefix):])
    except:
        raise TestFault(
            'Response for `persons` POST request has `Location` header in wrong format')
    return loc


def test1() -> None:
    body, _ = do_request(f'{HOST_URL}/persons', 'GET', 200)
    if not isinstance(body, list):
        raise TestFault('Response for `/persons` GET request is not an array')
    for person in body:
        if person.get('id') == None or person.get('name') == None:
            raise TestFault('One of returned persons has no mandatory fields')


def test2() -> None:
    deleteTestUser()
    id = createTestUser()

    body, _ = do_request(f'{HOST_URL}/persons', 'GET', 200)
    if TEST_USERNAME not in (x.get('name') for x in body):
        raise TestFault('Database does not contain created user')

    body, _ = do_request(f'{HOST_URL}/persons/{id}', 'GET', 200)

    do_request(f'{HOST_URL}/persons/{id}', 'DELETE', 204)

    if body.get('name') != TEST_USERNAME:
        raise TestFault('Created user has invalid name')
    if body.get('age') != TEST_AGE:
        raise TestFault('Created user has invalid name')
    if body.get('work') != TEST_WORK:
        raise TestFault('Created user has invalid name')
    if body.get('address') != None:
        raise TestFault('Created user has an address, but shouldn`t')


def test3():
    deleteTestUser()
    id = createTestUser()

    personPatch = PersonRequest(
        TEST_USERNAME, age=TEST_AGE2, address=None, work=None)
    do_request(f'{HOST_URL}/persons/{id}', 'PATCH', 200, personPatch.toJSON())

    body, _ = do_request(f'{HOST_URL}/persons/{id}', 'GET', 200)

    do_request(f'{HOST_URL}/persons/{id}', 'DELETE', 204)

    if body.get('name') != TEST_USERNAME:
        raise TestFault('Created user has invalid name')
    if body.get('age') != TEST_AGE2:
        raise TestFault('Created user has invalid name')
    if body.get('work') != TEST_WORK:
        raise TestFault('Created user has invalid name')
    if body.get('address') != None:
        raise TestFault('Created user has an address, but shouldn`t')


passed = None
try:
    test1()
    print('[OK] Test 1 passed')

    test2()
    print('[OK] Test 2 passed')

    test3()
    print('[OK] Test 3 passed')

    passed = True
except TestFault as e:
    print(f'ERROR: {e.fault_msg}')
    passed = False
except Exception as e:
    print(f'Unexpected exception: {e}')
    passed = False

if passed:
    print('[OK] All tests passed!')
else:
    print('Some tests failed!')
    exit(1)
