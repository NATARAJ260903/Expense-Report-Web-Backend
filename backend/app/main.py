from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, expenses, manager, finance

app = FastAPI(title="Expense Report Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(expenses.router)
app.include_router(manager.router)
app.include_router(finance.router)

@app.get("/")
def root():
    return {"message":"Expense API running"}
