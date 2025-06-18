from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from datetime import datetime
import os 

import re

def extract_phone(report_text):
    match = re.search(r"\b(?:Hospital Phone|Contact|Helpline|Customer Care)[^\d]*(\d{10})", report_text, re.IGNORECASE)
    return match.group(1) if match else None

def extract_doctor(report_text):
    match = re.search(r"(Reported by|Reviewed by|Referring Doctor)[:\-]?\s*(Dr\.?\s+[A-Za-z\s]+)", report_text, re.IGNORECASE)
    return match.group(2).strip() if match else None

def extract_patient_name(report_text):
    # Try to find a greeting like 'Hello Mr. Ali Asgar' or 'Hello Ms. Jane Doe'
    match = re.search(r"Hello\s+(Mr\.|Ms\.|Mrs\.|Dr\.)?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)", report_text)
    if match:
        return match.group(2).strip()
    else:
        # Fallback: Try to find "Hello <Name>" without honorifics
        match2 = re.search(r"Hello\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)", report_text)
        if match2:
            return match2.group(1).strip()
    return None

# Step 1: Load the prompt from file
def load_prompt(file_name: str) -> str:
    script_dir = os.path.dirname(os.path.abspath(__file__))  # folder where message_chain.py lives
    file_path = os.path.join(script_dir, file_name)
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

# Step 2: Modify get_message_chain to use loaded prompt
def get_message_chain(llm):
    prompt_text = load_prompt("prompt.txt")  # load from prompt.txt

    prompt = PromptTemplate(
        input_variables=["report_text", "patient_name", "start_date", "TODAY_DATE"],
        template=prompt_text
    )

    return LLMChain(llm=llm, prompt=prompt)

# Step 3: Your chain runner function remains same
def generate_plan(report_text, start_date, llm):
    patient_name = extract_patient_name(report_text) or "Patient"
    chain = get_message_chain(llm)
    phone = extract_phone(report_text)
    doctor = extract_doctor(report_text)
    return chain.run({
        "report_text": report_text[:5000],  # truncate if needed
        "patient_name": patient_name,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "TODAY_DATE": datetime.today().strftime("%Y-%m-%d"),
        "Phone": phone or "",
        "Doctor_Name": doctor or ""
    })

