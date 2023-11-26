from pydantic import BaseModel


class UserCredentials(BaseModel):
    username: str
    password: str

class Note(BaseModel):
    title:str
    desc:str
