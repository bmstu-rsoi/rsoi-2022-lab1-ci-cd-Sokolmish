from dataclasses import dataclass
import json
from typing import Dict, List, Union


def cleanNones(o):
    return {k: v for k,
            v in o.__dict__.items() if v is not None}


class ApiMessage:
    def toJSON(obj):
        return json.dumps(obj, separators=(',', ':'),
                          default=cleanNones)


def arrToJson(arr: List[ApiMessage]):
    return json.dumps([cleanNones(e) for e in arr], separators=(',', ':'))


@dataclass
class ErrorResponse(ApiMessage):
    msg: str


@dataclass
class ValidationErrorResponse(ApiMessage):
    msg: str
    errors: Dict[str, str]


@dataclass
class PersonResponse(ApiMessage):
    id: int
    name: str
    age: Union[int, None]
    address: Union[str, None]
    work: Union[str, None]


@dataclass
class PersonRequest(ApiMessage):
    name: str
    age: Union[int, None]
    address: Union[str, None]
    work: Union[str, None]
