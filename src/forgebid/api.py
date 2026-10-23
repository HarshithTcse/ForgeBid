
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ValidationError

from forgebid.ai_extractor import extract_rfp_with_ai
from forgebid.models import RFPDocument

app = FastAPI(
    title="ForgeBid API",
    description="AI-powered RFP analysis backend",
    version="0.1.0",
)


class AnalyzeRequest(BaseModel):
    rfp_text: str = Field(
        min_length=1,
        description="The text content of an RFP document",
    )


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ForgeBid API"}


@app.post("/analyze", response_model=RFPDocument)
def analyze_rfp(request: AnalyzeRequest):
    try:
        return extract_rfp_with_ai(request.rfp_text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(
            status_code=502,
            detail="Gemini returned data that failed validation.",
        ) from exc
    except Exception as exc:
        # Log the real error server-side; avoid exposing API details.
        print(f"RFP analysis failed: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=502,
            detail="RFP analysis failed. Check the server logs.",
        ) from exc
