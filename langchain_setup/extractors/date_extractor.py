from datetime import datetime
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

def get_date_chain(llm):
    prompt = PromptTemplate(
        input_variables=["report_text", "today_date"],
        template="""
Given the following lab report text, extract the final report date.
Use: Reported On > Report Date > Result Reported On > Date of Issue > Sample Collection Date > Test Performed Date.
If none found, return today’s date: {today_date}.

Lab Report:
{report_text}

Only return the date in YYYY-MM-DD format.
"""
    )
    return LLMChain(llm=llm, prompt=prompt)

def extract_start_date(report_text, llm):
    today = datetime.today().strftime("%Y-%m-%d")
    chain = get_date_chain(llm)
    response = chain.run({"report_text": report_text[:2000], "today_date": today})
    try:
        return datetime.strptime(response.strip(), "%Y-%m-%d")
    except:
        return datetime.today()