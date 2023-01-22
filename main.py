import os

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from list_manager import create_list, check_password, add_entry, remove_entry, get_entries, count_entries

app = FastAPI()


class NewList(BaseModel):
    password: str


class NewEntry(BaseModel):
    list_id: str
    list_password: str
    url: str


class RemoveEntry(BaseModel):
    list_id: str
    list_password: str
    entry_id: int


@app.post("/v1/list/create", status_code=201)
async def create_new_list(new_list: NewList):
    list_id = await create_list(new_list.password)
    return {"id": list_id}


@app.post("/v1/list/add", status_code=201)
async def add_list_entry(new_entry: NewEntry):
    password_valid = await check_password(new_entry.list_password, new_entry.list_id)
    if not password_valid:
        raise HTTPException(status_code=403, detail="Unauthorized")

    count = await count_entries(new_entry.list_id)

    if count >= 20:
        raise HTTPException(status_code=507, detail="A list can only have 20 elements")

    await add_entry(new_entry.url, new_entry.list_id)

    return {"message": "created"}


@app.delete("/v1/list/remove", status_code=200)
async def add_list_entry(entry: RemoveEntry):
    password_valid = await check_password(entry.list_password, entry.list_id)
    if not password_valid:
        raise HTTPException(status_code=403, detail="Unauthorized")

    await remove_entry(entry.list_id, entry.entry_id)
    return {"message": "removed"}


@app.get("/v1/list/{list_id}", status_code=200)
async def get_entry(list_id: str):
    results = await get_entries(list_id)
    count = await count_entries(list_id)
    return {"entries": results, "count": count}


if __name__ == "__main__":
    port = int(os.getenv('PORT'))
    uvicorn.run(app, host="0.0.0.0", port=port)
