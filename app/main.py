from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import auth, users, orders, categories, wallet

app = FastAPI(
    title="Self Market API",
    description="API для приложения Self Market",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

prefix = "/api/v1"
app.include_router(auth.router, prefix=prefix)
app.include_router(users.router, prefix=prefix)
app.include_router(orders.router, prefix=prefix)
app.include_router(categories.router, prefix=prefix)
app.include_router(wallet.router, prefix=prefix)

@app.get("/")
async def root():
    return {"message": "This page is not in use"}

def start_dev():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
