from pywebio.input import file_upload
from pywebio.output import put_text, put_html, put_row, put_column, put_button
from transformers import pipeline
from PyPDF2 import PdfReader
from io import BytesIO
from pywebio.session import run_js

# Load the summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def extract_text_from_pdf(pdf_bytes):
    """Extract text from a PDF file"""
    pdf_stream = BytesIO(pdf_bytes)  # Wrap bytes in a BytesIO object
    pdf_reader = PdfReader(pdf_stream)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def summarize_text():

    put_html("<h2>PDF Summarization Tool</h2>")
    put_text("Upload a PDF file to get its summary.")

    pdf_file = file_upload("Upload your PDF", accept="application/pdf")
    if not pdf_file:
        return  # Do nothing if no file is uploaded

    # Extract text from the uploaded PDF
    text = extract_text_from_pdf(pdf_file['content'])
    put_text("Text extracted from the PDF...")
    
    # Limit the input text for summarization
    max_input_size = 1024  # Adjust based on the model's context window
    input_text = text[:max_input_size]
    
    # Summarize the text
    put_text("Summarizing the text...")
    summary = summarizer(input_text, max_length=100, min_length=50, do_sample=False)
    
    # Display the summary
    put_html(f"<h3>Summary</h3><p>{summary[0]['summary_text']}</p>")

    put_column([
        put_html("<hr>"),
        put_row([put_button("Back to Upload", onclick=lambda: run_js('window.location.reload()'))])
    ])

# Run the PyWebIO application
if __name__ == "__main__":
    from pywebio import start_server
    start_server(summarize_text, port=8080)
