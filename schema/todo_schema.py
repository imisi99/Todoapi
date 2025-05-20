from pydantic import BaseModel, Field
from typing import Annotated, Optional



class CreateTodo(BaseModel):
    tasks: Annotated[str, Field(max_length=100)]
    note: Annotated[str, Field(max_length=100)]
    due: Annotated[str, Field()]



class UpdateTodo(BaseModel):
    tasks: Annotated[str, Field(max_length=100)]
    completed: Annotated[bool, Field(Optional)]
    note: Annotated[str, Field(max_length=100)]
    due: Annotated[str, Field]
    user_id: Annotated[int, Field(Optional)]

