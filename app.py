import streamlit as st
from pypdf import PdfReader
from google import genai
import os

st.set_page_config(
    page_title="CargoDoc AI | Ocean B/L & Document Auditor",
    page_icon="🚢",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .main { background-color: #0b1120; }
    h1, h2, h3 { color: #38bdf8 !important; }
    .stAlert { border-radius: 12px; }
    </style>
""", unsafe_allow_html=True)

st.title("🚢 Global Trade & Ocean B/L Document Auditor")
st.markdown("""
**Autonomous Shipping Compliance Engine** for freight forwarders, EXIM operators, and logistics teams.
Upload an **Ocean Bill of Lading (B/L)**, **Commercial Invoice**, or **Packing List** to audit cargo discrepancies, weight balances, and Incoterm liabilities.
""")

# Sidebar API Setup
st.sidebar.header("🔑 Authentication")
api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

# Test Sample Generator (For Instant Auditing)
st.sidebar.markdown("---")
st.sidebar.subheader("📋 Load Sample B/L")
use_sample = st.sidebar.button("Load Discrepancy Test Sample")

sample_bl_text = """
BILL OF LADING FOR OCEAN TRANSPORT
B/L NUMBER: MSCU-BOM-982341
CARRIER: Mediterranean Shipping Company (MSC)
VESSEL / VOYAGE: MSC CLARA / V.2408W
PORT OF LOADING: Nhava Sheva (JNPT), India
PORT OF DISCHARGE: Port of Rotterdam, Netherlands
INCOTERM: CIF Rotterdam (Incoterms 2020)

SHIPPER (CONSIGNOR):
Apex Global Engineering Exports Ltd.
Andheri East, Mumbai, MH 400069, India

CONSIGNEE:
Rotterdam Precision Machinery B.V.
Haven 1024, 3008 AB Rotterdam, Netherlands

CARGO DESCRIPTION:
1x40' High Cube Container (MSCU-7749102 / Seal: SL-88391)
Declared Goods: Industrial CNC Precision Lathe Assemblies
HS CODE: 8458.11.00
QUANTITY: 14 Wooden Crates

WEIGHT SPECIFICATIONS:
Declared Gross Weight: 24,850.00 KGS
Declared Net Weight: 22,400.00 KGS
Measurement: 48.50 CBM

FREIGHT & CLAUSES:
Freight Prepaid.
Clean on Board date: 14-SEPT-2026.
Note on packing: 1 crate found with outer strap seal compromised prior to container loading.
"""

uploaded_file = st.file_uploader("Upload Shipping Document (PDF)", type=["pdf"])

def extract_text(file):
    reader = PdfReader(file)
    extracted = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            extracted += text + "\n"
    return extracted

document_text = ""
if uploaded_file:
    document_text = extract_text(uploaded_file)
elif use_sample:
    document_text = sample_bl_text

if document_text:
    st.success("Document loaded successfully into memory.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📄 Raw Shipping Document Text")
        st.text_area("Extracted Cargo Text", document_text, height=450)
        
    with col2:
        st.subheader("🔍 Automated Trade Compliance Audit")
        
        if st.button("🚀 Run Live Audit & Compliance Check", use_container_width=True):
            if not api_key:
                st.error("Please enter your Gemini API Key in the left sidebar to proceed.")
            else:
                with st.spinner("Analyzing shipping data, container integrity, and trade compliance..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        
                        prompt = f"""
You are an expert Ocean Freight Documentation Specialist, Customs Broker, and Logistics Auditor.
Conduct a rigorous customs & operations audit on this shipping document:

Shipping Document:
\"\"\"
{document_text}
\"\"\"

Produce your findings strictly in the following Markdown format:

### 1. Document Identity & Voyage Details
- **Document Type & Number**:
- **Ocean Carrier & Vessel**:
- **Route**: [Port of Loading] -> [Port of Discharge]
- **Parties**: Shipper vs Consignee

### 2. Core Shipping Matrix
| Parameter | Declared Value | Compliance Status |
|---|---|---|
| Container & Seal # | ... | ... |
| HS Code | ... | ... |
| Gross / Net Weight | ... | ... |
| Incoterm (2020) | ... | ... |

### 3. Discrepancy & Risk Detection
- Identify any discrepancies, cargo condition remarks (e.g. compromised seals or packaging), weight ratio sanity, or clause compliance issues.

### 4. Customs Clearance Verdict
- Give an explicit verdict: `[🟢 READY FOR CLEARANCE]`, `[🟡 ACTION REQUIRED]`, or `[🔴 SHIPMENT HOLD / CRITICAL DISCREPANCY]`.
- List 2 to 3 actionable next steps for the freight operations coordinator.
"""
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt,
                        )
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"Execution Error: {str(e)}")
