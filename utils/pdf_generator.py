from fpdf import FPDF
import tempfile

def create_pdf_itinerary(name: str, base_text: str, logo_path=None) -> bytes:
    """Generates PDF and ensures bytes output (not bytearray)"""
    pdf = FPDF()
    pdf.add_page()
    
    # 1. Set font and replace special characters
    pdf.set_font("Arial", size=12)
    safe_text = (
        base_text.replace("{name}", name)
        .replace("₹", "Rs.")
        .replace("€", "EUR")
        .replace("•", "-")
    )
    
    # 2. Optional logo handling
    if logo_path:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                tmp.write(logo_path.read())
                pdf.image(tmp.name, x=10, y=8, w=30)
        except:
            pass
    
    # 3. Add content
    pdf.cell(0, 10, f"{name}'s Itinerary", ln=True)
    pdf.multi_cell(0, 10, safe_text)
    
    # 4. Ensure bytes output
    pdf_output = pdf.output(dest='S')
    return bytes(pdf_output) if isinstance(pdf_output, bytearray) else pdf_output