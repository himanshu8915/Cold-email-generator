import streamlit as st
import pandas as pd
import os
import time
from utils.email_generator import generate_persuasive_email
from utils.pdf_generator import create_pdf_itinerary
from utils.email_sender import send_email  # Using Gmail API
from dotenv import load_dotenv

load_dotenv()

# Page Config
st.set_page_config(
    page_title="Luxury Hotel Campaign Manager", 
    layout="wide",
    menu_items={
        'About': "### 🏨 End-to-End Email Campaign Tool\nSafe and secure bulk email sender"
    }
)
st.title("✨ Luxury Hotel Email Campaign")

# --- Authentication Check ---
def check_auth():
    """Verifies Gmail API credentials"""
    if not os.path.exists('token.json'):
        with st.sidebar:
            st.error("🔑 Authentication Required")
            if st.button("Authenticate with Gmail"):
                try:
                    from utils.email_sender import get_gmail_service
                    get_gmail_service()  # Will create token.json
                    st.rerun()
                except Exception as e:
                    st.error(f"Authentication failed: {str(e)}")
        return False
    return True

# --- File Upload ---
def get_assets():
    with st.sidebar:
        st.header("📁 Upload Assets")
        csv_file = st.file_uploader(
            "Guest Data (CSV)", 
            type=["csv"],
            help="Requires columns: name, email, interests"
        )
        itinerary_file = st.file_uploader(
            "Itinerary Template (TXT)", 
            type=["txt"],
            help="Use {name} for personalization"
        )
        logo_file = st.file_uploader(
            "Hotel Logo", 
            type=["png", "jpg"],
            accept_multiple_files=False
        )
        poster_file = st.file_uploader(  # NEW: Poster upload
            "Marketing Poster (PNG)", 
            type=["png"],
            help="Will be attached to emails"
        )
        
        st.header("🔗 URLs")
        booking_link = st.text_input(
            "Booking Page", 
            value="https://your-hotel.com/book"
        )
        itinerary_link = st.text_input(
            "Personalization Tool", 
            value="https://your-hotel.com/personalize"
        )
        
        return csv_file, itinerary_file, logo_file, poster_file, booking_link, itinerary_link

# --- Email Preview ---
def show_email_preview(content, pdf_data):
    st.subheader("✉️ Email Preview")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(content, unsafe_allow_html=True)
    
    with col2:
        with st.expander("📄 Itinerary Preview"):
            # Ensure bytes format
            pdf_bytes = bytes(pdf_data) if isinstance(pdf_data, bytearray) else pdf_data
            st.download_button(
                label="Download Sample",
                data=pdf_bytes,
                file_name="preview_itinerary.pdf",
                mime="application/pdf"
            )
    
    return st.toggle("✅ Approve for sending", value=False)

# --- Main Workflow ---
def main():
    # Authentication check
    if not check_auth():
        return
    
    # Get user inputs
    csv_file, itinerary_file, logo_file, poster_file, booking_link, itinerary_link = get_assets()
    
    if not (csv_file and itinerary_file):
        st.warning("Please upload both CSV and itinerary files to begin")
        return
    
    try:
        # Load data
        customers = pd.read_csv(csv_file)
        base_itinerary = itinerary_file.read().decode("utf-8")
        
        # Generate sample content
        with st.spinner("🔮 Creating campaign preview..."):
            sample = customers.iloc[0]
            
            # Create sample PDF
            pdf_preview = create_pdf_itinerary(
                name=sample['name'],
                base_text=base_itinerary,
                logo_path=logo_file
            )
            
            # Generate sample email
            email_preview = generate_persuasive_email(
                name=sample['name'],
                interests=sample.get('interests', ''),
                booking_link=booking_link,
                itinerary_link=itinerary_link
            )
        
        # Approval workflow
        if show_email_preview(email_preview, pdf_preview):
            st.divider()
            
            # Double confirmation
            col1, col2 = st.columns(2)
            with col1:
                send_btn = st.button(
                    "🚀 Launch Campaign", 
                    type="primary",
                    use_container_width=True
                )
            with col2:
                confirmed = st.checkbox(
                    "I confirm this will send REAL emails",
                    help="Verifies you have recipient consent"
                )
            
            if send_btn and confirmed:
                progress_bar = st.progress(0)
                status = st.empty()
                success_count = 0
                
                # Process all recipients
                for i, row in customers.iterrows():
                    # Generate personalized content
                    current_pdf = create_pdf_itinerary(
                        row['name'], 
                        base_itinerary, 
                        logo_file
                    )
                    current_email = generate_persuasive_email(
                        row['name'],
                        row.get('interests', ''),
                        booking_link,
                        itinerary_link
                    )
                    
                    # Type safety check
                    if isinstance(current_pdf, bytearray):
                        current_pdf = bytes(current_pdf)
                    
                    # Prepare poster bytes if uploaded
                    poster_bytes = None
                    if poster_file:
                        poster_file.seek(0)  # Reset file pointer
                        poster_bytes = poster_file.read()
                    
                    # Send email with both attachments
                    success, msg = send_email(
                        to_email=row['email'],
                        subject=f"Your Luxury Experience, {row['name']}!",
                        html_content=current_email,
                        pdf_bytes=current_pdf,
                        poster_bytes=poster_bytes
                    )
                    
                    # Update UI
                    if success:
                        status.success(f"Sent to {row['email']}")
                        success_count += 1
                    else:
                        status.error(f"Failed: {msg}")
                    
                    progress_bar.progress((i + 1) / len(customers))
                    time.sleep(1)  # Rate limiting
                
                # Completion message
                st.balloons()
                if success_count == len(customers):
                    st.success(f"✨ Perfect! All {success_count} emails sent")
                else:
                    st.warning(
                        f"Sent {success_count}/{len(customers)} emails. "
                        f"{len(customers) - success_count} failed."
                    )
                
                # Log completion
                with open("campaign_log.txt", "a") as f:
                    f.write(f"{time.ctime()}: Sent {success_count} emails\n")
            
            elif send_btn and not confirmed:
                st.error("Please check the confirmation box to proceed")
    
    except Exception as e:
        st.error(f"❌ System Error: {str(e)}")
        st.stop()

if __name__ == "__main__":
    main()