from langchain_community.document_loaders import PyPDFLoader

def load_lab_report(pdf_path):
    loader = PyPDFLoader(pdf_path)
    pages = loader.load_and_split()
    return "\n".join([page.page_content for page in pages])