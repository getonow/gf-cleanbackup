from dotenv import load_dotenv
load_dotenv()
import os
import openai
import gspread
from google.oauth2.service_account import Credentials
import plotly.graph_objects as go
from app.models import ChatResponse
import re
import json

# Set up OpenAI client for v1+ API
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Google Sheets setup (load from environment variable for Railway/prod)
SHEET_ID = "1gSaOWf_KyZPEzjvnYrUm2KxRzUe9-UqrMBdtKQOmn3U"
SHEET_NAME = "MASTER_FILE_ACMECo"
SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials_info = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])
creds = Credentials.from_service_account_info(credentials_info, scopes=SCOPES)
gc = gspread.authorize(creds)
sh = gc.open_by_key(SHEET_ID)
worksheet = sh.worksheet(SHEET_NAME)

# Helper: parse part number and % increase from message
def parse_input(message):
    part_match = re.search(r"PA-\d+", message)
    pct_match = re.search(r"(\d+)%", message)
    part = part_match.group(0) if part_match else None
    pct = float(pct_match.group(1)) if pct_match else None
    return part, pct

# Helper: get part row from sheet
def get_part_row(part_number):
    records = worksheet.get_all_records()
    for row in records:
        if str(row.get("PartNumber")).strip() == part_number:
            return row
    return None

# Main agent logic
def generate_response(message: str) -> ChatResponse:
    part_number, pct_increase = parse_input(message)
    if not part_number or not pct_increase:
        return ChatResponse(text="Could not parse part number or % increase.", chart1="{}", chart2="{}")
    row = get_part_row(part_number)
    if not row:
        return ChatResponse(text=f"Part {part_number} not found in master file.", chart1="{}", chart2="{}")

    # Compose prompt for OpenAI
    prompt = f"""
You are BIGPICTURE, an expert negotiation and procurement AI. Given the following part and supplier data, and a supplier price increase request, analyze the impact and provide a negotiation strategy.\n
User message: {message}\n
Part data: {json.dumps(row)}\n
Please:
- Summarize the situation and impact of the price increase for 2025 (annual and monthly)
- Provide negotiation recommendations
- Output only the text response, not a chart
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are BIGPICTURE, an expert negotiation and procurement AI."},
            {"role": "user", "content": prompt}
        ]
    )
    text = response.choices[0].message.content.strip()

    # Prepare data for chart
    price_cols = [col for col in row.keys() if col.startswith("price") and len(col) == 11]
    price_cols.sort(key=lambda x: (x[-4:], x[5:8]))  # sort by year, then month
    prices = [row[c] for c in price_cols]
    months = price_cols

    mkt_cols = [col for col in row.keys() if col.startswith("Pricemktindex")]
    mkt_cols.sort(key=lambda x: (x[-4:], x[13:16]))
    mkt_prices = [row[c] for c in mkt_cols if row[c] not in (None, "")]
    mkt_months = [c.replace("Pricemktindex", "price") for c in mkt_cols if row[c] not in (None, "")]

    # Plotly chart as JSON
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=prices, mode='lines+markers', name='Company Price'))
    if mkt_prices:
        fig.add_trace(go.Scatter(x=mkt_months, y=mkt_prices, mode='lines+markers', name='Market Index'))
    fig.update_layout(title="Price Evolution", xaxis_title="Month", yaxis_title="Price", legend_title="Legend")
    chart_json = fig.to_json()

    return ChatResponse(text=text, chart1=chart_json, chart2="{}") 