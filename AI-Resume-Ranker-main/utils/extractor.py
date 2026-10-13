import io
import fitz  # PyMuPDF
try:
    import docx
except ImportError:
    docx = None

def extract_text(file):
    """
    Extract text from uploaded file object (.pdf, .docx, or .txt).
    Handles byte streams and normalizes whitespace.
    """
    filename = getattr(file, "name", "").lower()
    
    if filename.endswith(".docx"):
        return extract_text_from_docx(file)
    elif filename.endswith(".txt"):
        return extract_text_from_txt(file)
    else:
        # Default to PDF parser
        return extract_text_from_pdf(file)

def extract_text_from_pdf(file):
    """Extract text from PDF using PyMuPDF with text sanitization."""
    try:
        content = file.read() if hasattr(file, "read") else file
        if hasattr(file, "seek"):
            file.seek(0)
            
        doc = fitz.open(stream=content, filetype="pdf")
        text_parts = []
        for page in doc:
            page_text = page.get_text("text")
            if page_text:
                text_parts.append(page_text)
                
        full_text = "\n".join(text_parts).strip()
        return full_text if full_text else None
    except Exception as e:
        print(f"Error reading PDF: {str(e)}")
        return None

def extract_text_from_docx(file):
    """Extract text from DOCX file."""
    try:
        content = file.read() if hasattr(file, "read") else file
        if hasattr(file, "seek"):
            file.seek(0)
            
        if docx is None:
            return None
            
        doc = docx.Document(io.BytesIO(content))
        text_parts = [p.text for p in doc.paragraphs if p.text.strip()]
        
        # Also extract table text if any
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    text_parts.append(row_text)
                    
        full_text = "\n".join(text_parts).strip()
        return full_text if full_text else None
    except Exception as e:
        print(f"Error reading DOCX: {str(e)}")
        return None

def extract_text_from_txt(file):
    """Extract text from plain text file."""
    try:
        content = file.read() if hasattr(file, "read") else file
        if hasattr(file, "seek"):
            file.seek(0)
            
        if isinstance(content, bytes):
            try:
                return content.decode("utf-8")
            except UnicodeDecodeError:
                return content.decode("latin-1", errors="ignore")
        return str(content)
    except Exception as e:
        print(f"Error reading TXT: {str(e)}")
        return None