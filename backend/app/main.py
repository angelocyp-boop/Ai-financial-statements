from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Base, engine
from app.routers import auth, firms, clients, engagements, trial_balance, mapping, statements, disclosures, validation, exports

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered IFRS financial statement automation platform",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in [
    auth.router,
    firms.router,
    clients.router,
    engagements.router,
    trial_balance.router,
    mapping.router,
    statements.router,
    disclosures.router,
    validation.router,
    exports.router,
]:
    app.include_router(router, prefix="/api")


@app.get("/")
def root():
    return {"service": settings.APP_NAME, "version": settings.APP_VERSION}


@app.get("/health")
def health():
    return {"status": "ok"}
