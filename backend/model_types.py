from dataclasses import dataclass, fields as datafields


@dataclass
class Meal:
    id: int
    calories:  int
    protein: int
    user_id: int
    created_at: str


@dataclass
class User:
    username: str


@dataclass
class Account:
    pass


def dataclass_from_dict(klass, dikt):
    try:
        fieldtypes = {f.name: f.type for f in datafields(klass)}
        return klass(**{f: dataclass_from_dict(fieldtypes[f], dikt[f]) for f in dikt})
    except:
        return dikt
