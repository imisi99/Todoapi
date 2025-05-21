from pydantic import BaseModel, Field
from typing import Annotated, Optional



class CreateTodo(BaseModel):
    tasks: Annotated[str, Field(max_length=50)]
    note: Annotated[str, Field(max_length=50)]



class UpdateTodo(BaseModel):
    tasks: Annotated[str, Field(max_length=50)]
    completed: Annotated[bool, Field(Optional)]
    note: Annotated[str, Field(max_length=50)]
    due: Annotated[Da]
