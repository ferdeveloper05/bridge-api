from pydantic import BaseModel, Field


class UserRegister(BaseModel): 
    username: str = Field(title="Nombre de Usuario", min_length=3)
    password: str = Field(title="Password de Usuario", min_length=5, max_length=10)
    
class UserLogin(BaseModel): 
    username: str
    password: str
    
class UserResponse(BaseModel): 
    username: str
    registered: bool