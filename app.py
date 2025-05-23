import base64
import io
import fitz  # PyMuPDF
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import re

# Configure Gemini API
genai.configure(api_key="AIzaSyCcoQ40u_iM1BIvp26iLqVTWdHp3Ky0TAw")

app = FastAPI()

# Allow CORS (so Wix frontend can access it)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prompt templates
input_prompt1 = "Analyze the resume for general job-fit in fields like tech, business, finance, and agriculture."
input_prompt2 = "Give detailed suggestions to improve this resume in terms of formatting, ATS friendliness, and professional standards."
input_prompt3 = "Compare this resume to a generic job description and provide a match percentage with reasons."

# Combined into a master prompt
master_prompt = f"""
You are a highly skilled HR professional, career coach, and ATS expert.

1. {input_prompt1}
2. {input_prompt2}
3. {input_prompt3}

Provide a detailed report that includes:
- Job-fit analysis
- Improvement suggestions
"""

# Function to extract match percentage
# def extract_match_percentage(response_text):
#     match = re.search(r"Match Percentage:\s*(\d+)%", response_text)
#     return int(match.group(1)) if match else 0

# Main endpoint
@app.post("/evaluate")
async def evaluate_resume(base64_pdf: str = Form(...)):
    # Gemini expects jpeg image of first page
    try:
        pdf_bytes = base64.b64decode(base64_pdf)
        pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        first_page = pdf_doc[0].get_pixmap()
        img_byte_arr = io.BytesIO(first_page.tobytes("jpeg"))
        image_base64 = base64.b64encode(img_byte_arr.getvalue()).decode()
    except Exception as e:
        return {"error": f"PDF processing failed: {str(e)}"}

    # Send to Gemini
    default_input_text = "Analyze this resume carefully:"
    model = genai.GenerativeModel('gemini-1.5-flash')
    try:
        response = model.generate_content([
            default_input_text,
            {"mime_type": "image/jpeg", "data": image_base64},
            master_prompt
        ])
        response_text = response.text
    except Exception as e:
        return {"error": f"Gemini API error: {str(e)}"}

    return {
        "response": response_text,
       
    }




