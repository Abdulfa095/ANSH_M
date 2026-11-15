from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import api_router

app = FastAPI(
    title="ANSH-M Agriculture Intelligence System",
    description="AI-powered Price Prediction and Mandi Optimization",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for prototype (or specific frontend URL)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Router
app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    from .db.database import engine
    from .db import models
    models.Base.metadata.create_all(bind=engine)
    
    from .services.scheduler import start_scheduler
    start_scheduler()

@app.get("/")
def read_root():
    return {"message": "ANSH-M API is running. Visit /docs for Swagger UI."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
