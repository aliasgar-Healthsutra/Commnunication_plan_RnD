from langchain_google_genai import ChatGoogleGenerativeAI
from loaders.pdf_loader import load_lab_report
from extractors.date_extractor import extract_start_date
from planners.scheduler import generate_schedule
from chains.message_chain import generate_plan
from utils.save_csv import save_csv
import os
from dotenv import load_dotenv
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3,google_api_key=gemini_api_key )

def run_pipeline(pdf_path):
    report_text = load_lab_report(pdf_path)
    start_date = extract_start_date(report_text, llm)
    csv_plan = generate_plan(report_text, start_date, llm)
    save_csv(csv_plan)
    print("Communication Plan saved ")

run_pipeline("../reports/sugar-12-24.pdf")


# import google.generativeai as genai

# # Set your API key
# genai.configure(api_key=gemini_api_key)

# # List available models
# for model in genai.list_models():
#     print(model.name, model.supported_generation_methods)
