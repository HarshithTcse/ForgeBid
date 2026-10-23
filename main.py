
from forgebid.ai_extractor import extract_rfp_with_ai

sample_rfp = """
Request for Proposal: College Website Development

Requirements:
- The website must use HTTPS encryption.
- The vendor must provide maintenance support for one year.
- The proposal must include a detailed pricing breakdown.

Evaluation Criteria:
- Technical quality
- Cost effectiveness
- Vendor experience
"""

try:
    result = extract_rfp_with_ai(sample_rfp)
    print("SUCCESS: Gemini responded!")
    print("\nExtracted RFP data:\n")
    print(result.model_dump_json(indent=2))
except Exception as error:
    print(f"Gemini test failed: {type(error).__name__}: {error}")
