
from pathlib import Path

from forgebid.evidence_analysis import analyze_rfp_evidence
from forgebid.go_nogo import evaluate_bid_readiness
from tempfile import NamedTemporaryFile
from forgebid.evidence_retrieval import retrieve_evidence_for_requirement
from forgebid.knowledge_base import CompanyKnowledgeBase
from forgebid.models import Requirement
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field, ValidationError
from forgebid.models import (
    BidReadinessAssessment,
    RFPAnalysisReport,
    RFPDocument,
)
from forgebid.ai_extractor import extract_rfp_with_ai
from forgebid.bid_readiness import assess_bid_readiness
from forgebid.models import BidReadinessAssessment, RFPDocument
from forgebid.pdf_reader import extract_text_from_pdf


class EvidenceRetrievalRequest(BaseModel):
    requirement: Requirement
    top_k: int = Field(default=3, ge=1, le=10)
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
    """Check whether the ForgeBid API is running."""
    return {
        "status": "healthy",
        "service": "ForgeBid API",
    }


@app.post("/analyze", response_model=RFPDocument)
def analyze_rfp(request: AnalyzeRequest):
    """Extract structured RFP information from text using Gemini."""
    try:
        return extract_rfp_with_ai(request.rfp_text)

    except ValidationError as exc:
        raise HTTPException(
            status_code=502,
            detail="Gemini returned data that failed validation.",
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        print(f"RFP analysis failed: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=502,
            detail="RFP analysis failed. Check the server logs.",
        ) from exc


@app.post("/upload-pdf", response_model=RFPDocument)
def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF and extract structured RFP information."""
    if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF file.",
        )

    temp_path = None

    try:
        content = file.file.read()

        if not content:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty.",
            )

        with NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(content)
            temp_path = Path(temp_file.name)

        rfp_text = extract_text_from_pdf(temp_path)
        return extract_rfp_with_ai(rfp_text)

    except HTTPException:
        raise

    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except ValidationError as exc:
        raise HTTPException(
            status_code=502,
            detail="Gemini returned data that failed validation.",
        ) from exc

    except Exception as exc:
        print(f"PDF analysis failed: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=502,
            detail="PDF analysis failed. Check the server logs.",
        ) from exc

    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)

        file.file.close()


@app.post(
    "/assess-readiness",
    response_model=BidReadinessAssessment,
)
def assess_readiness(rfp: RFPDocument):
    """Assess bid readiness using deterministic rules."""
    return assess_bid_readiness(rfp)

@app.post(
    "/analyze-pdf",
    response_model=RFPAnalysisReport,
)
def analyze_pdf(file: UploadFile = File(...)):
    """Extract an RFP from PDF and assess its bid readiness."""
    if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF file.",
        )

    temp_path = None

    try:
        content = file.file.read()

        if not content:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty.",
            )

        with NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(content)
            temp_path = Path(temp_file.name)

        rfp_text = extract_text_from_pdf(temp_path)
        extracted_rfp = extract_rfp_with_ai(rfp_text)
        readiness = assess_bid_readiness(extracted_rfp)

        return RFPAnalysisReport(
            extracted_rfp=extracted_rfp,
            readiness_assessment=readiness,
        )

    except HTTPException:
        raise

    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except ValidationError as exc:
        raise HTTPException(
            status_code=502,
            detail="Gemini returned data that failed validation.",
        ) from exc

    except Exception as exc:
        print(f"Combined PDF analysis failed: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=502,
            detail="PDF analysis failed. Check the server logs.",
        ) from exc

    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)

        file.file.close()

@app.post("/retrieve-evidence")
def retrieve_evidence_endpoint(
    request: EvidenceRetrievalRequest,
):
    try:
        knowledge_base = CompanyKnowledgeBase()

        if knowledge_base.collection.count() == 0:
            raise HTTPException(
                status_code=409,
                detail="Knowledge base is empty. Index documents first.",
            )

        return retrieve_evidence_for_requirement(
            requirement=request.requirement,
            knowledge_base=knowledge_base,
            top_k=request.top_k,
        )

    except HTTPException:
        raise
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


class EvidenceAnalysisRequest(BaseModel):
    rfp: RFPDocument
    top_k: int = Field(default=3, ge=1, le=10)
    max_distance: float = Field(default=0.45, ge=0.0)


@app.post("/analyze-evidence")
def analyze_evidence_endpoint(request: EvidenceAnalysisRequest):
    try:
        knowledge_base = CompanyKnowledgeBase()

        if knowledge_base.collection.count() == 0:
            raise HTTPException(
                status_code=409,
                detail="Knowledge base is empty. Index documents first.",
            )

        return analyze_rfp_evidence(
            rfp=request.rfp,
            knowledge_base=knowledge_base,
            top_k=request.top_k,
            max_distance=request.max_distance,
        )

    except HTTPException:
        raise
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


class GoNoGoRequest(BaseModel):
    evidence_report: dict
@app.post("/evaluate-bid")
def evaluate_bid_endpoint(request: GoNoGoRequest):
    try:
        return evaluate_bid_readiness(request.evidence_report)
    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc