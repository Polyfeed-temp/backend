from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
app = FastAPI(swagger_ui_parameters={"syntaxHighlight": False})

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

print("hi")
@app.get("/api")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}