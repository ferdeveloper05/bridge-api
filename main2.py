from fastapi import FastAPI, Depends


app = FastAPI()


def parametros_paginacion(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

@app.get("/items/")
async def read_items(commons: dict = Depends(parametros_paginacion)):
    return commons