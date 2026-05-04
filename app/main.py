from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError
from app.database import Base, engine
from app.routes import auth_routes, calc_routes, report_routes

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(_: FastAPI):
    print("Application startup complete.")
    try:
        yield
    finally:
        print("Goodbye, shutting down...")


app = FastAPI(title="Calculator App", lifespan=lifespan)

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})

@app.exception_handler(PydanticValidationError)
async def validation_error_handler(request: Request, exc: PydanticValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

app.include_router(auth_routes.router)
app.include_router(calc_routes.router)
app.include_router(report_routes.router)

@app.get("/")
def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse("/login")


@app.get("/.well-known/appspecific/com.chrome.devtools.json", include_in_schema=False)
def chrome_devtools_probe():
    return Response(status_code=204)


if __name__ == "__main__":
    import os
    import uvicorn

    try:
        # On Windows, reload mode runs a subprocess that can print KeyboardInterrupt tracebacks on Ctrl+C.
        # Keep reload off by default for clean shutdown logs; allow opt-in via env var.
        reload_enabled = os.getenv("UVICORN_RELOAD", "false").lower() in {"1", "true", "yes"}
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=reload_enabled)
    except KeyboardInterrupt:
        print("Goodbye, shutting down...")
