import logging
from datetime import datetime, timezone
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings, Base, engine, get_db
from app.core.logging import setup_logging
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.common import Token, UserCreate, UserResponse

from app.api import news, image, reports, health, users

# 1. Setup logs
setup_logging()
logger = logging.getLogger("truthlens.main")

# 2. Programmatically create tables if they don't exist
try:
    logger.info("Initializing SQLite database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified.")
except Exception as e:
    logger.critical(f"Failed to initialize database tables: {e}")

# 3. Create FastAPI App
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="TruthLens AI API - Verify truth in news, claims and images in real-time.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 4. Enable CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:4000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Inline Auth Router ────────────────────────────────────────────────────────
auth_router = APIRouter(prefix="/auth", tags=["auth"])

def _authenticate_user(email: str, password: str, db: Session) -> User:
    """Shared login logic. Raises HTTPException on failure."""
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@auth_router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    exists = db.query(User.id).filter(User.email == user_in.email).first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered.",
        )
    # Use provided password; default password is 123456 if none supplied
    raw_password = user_in.password if user_in.password else "123456"
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(raw_password),
        full_name=getattr(user_in, "full_name", None),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@auth_router.post("/login", response_model=Token)
def login(user_in: UserCreate, db: Session = Depends(get_db)):
    user = _authenticate_user(user_in.email, user_in.password, db)
    # Track last login timestamp
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    return {"access_token": create_access_token(subject=user.email), "token_type": "bearer"}

@auth_router.post("/login-oauth", response_model=Token)
def login_oauth(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = _authenticate_user(form_data.username, form_data.password, db)
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    return {"access_token": create_access_token(subject=user.email), "token_type": "bearer"}

# 5. Include API routers
app.include_router(auth_router, prefix="/api")
app.include_router(news.router, prefix="/api")
app.include_router(image.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(health.router, prefix="/api")
app.include_router(users.router, prefix="/api")

@app.get("/")
def root():
    return {
        "app": settings.PROJECT_NAME,
        "status": "online",
        "documentation": "/docs"
    }
