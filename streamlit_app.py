import streamlit as st
import datetime as dt
import pytz
import gspread
from google.oauth2.service_account import Credentials

#
# 1) PAGE CONFIG + BRAND STYLING
#
st.set_page_config(
    page_title="Burgo's Briefing App",
    page_icon="🌟",
    layout="centered"
)

BRAND_CSS = """
<style>
/* Load Roboto + Oswald from Google Fonts */
@import url('https://fonts.googleapis.com/css?family=Roboto:300,400,500,700,900');
@import url('https://fonts.googleapis.com/css?family=Oswald:400,700');

/* :root variables for Motley Fool color palette */
:root {
  --fool-gold: #ffb81c;
  --fool-bronze: #cf7f00;
  --fool-orange: #ff6900;
  --fool-red:    #f9423a;
  --fool-magenta:#e31c79;
  --fool-purple: #981e97;
  --fool-blue:   #485cc7;
  --fool-cyan:   #0095c8;
  --fool-green:  #43b02a;
  --fool-midgray:#53565a;
  --fool-black:  #000000;
}

/* Override default font to Roboto for nearly all text */
html, body, [class*="css"]  {
  font-family: 'Roboto', sans-serif;
  color: var(--fool-midgray);
  background-color: #ffffff;
}

/* Streamlit's main title or h1 classes */
h1, .stTitle {
  font-family: 'Oswald', sans-serif;
  color: var(--fool-red);
  font-weight: 700;
  margin-bottom: 0.5rem;
}

/* Streamlit's subheader or h2 classes */
h2, .stSubtitle {
  font-family: 'Oswald', sans-serif;
  color: var(--fool-orange);
  margin-top: 1rem;
}

/* Style the default st.button */
div.stButton > button {
  background-color: var(--fool-green);
  color: #fff;
  border-radius: 4px;
  border: none;
  font-weight: 500;
  padding: 0.6rem 1.2rem;
  margin-top: 1rem;
  cursor: pointer;
}
div.stButton > button:hover {
  background-color: #2a8b1c; /* darker green on hover */
}

/* Style st.success messages to use the brand green */
.stAlert > div[role="alert"] {
  background-color: #e3f6d8 !important;
  border-left: 0.25rem solid var(--fool-green) !important;
  color: var(--fool-midgray);
}
</style>
"""
st.markdown(BRAND_CSS, unsafe_allow_html=True)

#
# 2) SET UP GOOGLE SHEETS CLIENT
#
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = st.secrets["service_account"]  # Must match your secrets.toml or Streamlit Cloud secrets
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
client = gspread.authorize(creds)

# Your Spreadsheet ID here:
spreadsheet_id = "1BzTJgX7OgaA0QNfzKs5AgAx2rvZZjDdorgAz0SD9NZg"
sheet = client.open_by_key(spreadsheet_id)

#
# 3) IMPORT YOUR SCRIPTS THAT DO THE REAL WORK
#
from data_retrieval_storage_news_engine import main as retrieve_and_store_data
from step2_summarisation_with_easier_reading import generate_summary

#
# 4) HELPER FUNCTIONS FOR UTC TIMESTAMPS
#

def get_last_run_info(sheet_obj):
    """
    Reads the 'Metadata' worksheet for last-run time (UTC) and summary text.
    Returns (last_run_utc, last_summary_text) where last_run_utc is tz-aware in UTC.
    """
    metadata_ws = sheet_obj.worksheet("Metadata")  # or your chosen sheet name

    last_run_time_str = metadata_ws.cell(2, 1).value  # A2
    last_summary_text = metadata_ws.cell(2, 2).value  # B2

    if last_run_time_str:
        # Parse the string (e.g., "2025-03-16 10:30:00") into a naive datetime
        naive_dt = dt.datetime.strptime(last_run_time_str, "%Y-%m-%d %H:%M:%S")
        # Attach UTC timezone
        last_run_utc = pytz.utc.localize(naive_dt)
    else:
        last_run_utc = None

    return last_run_utc, last_summary_text


def set_last_run_info(sheet_obj, summary_text):
    """
    Stores the new run time (UTC) plus summary in row 2 of 'Metadata' sheet.
    """
    metadata_ws = sheet_obj.worksheet("Metadata")

    # 1) Current time in UTC
    now_utc = dt.datetime.utcnow()
    # 2) Format as "YYYY-MM-DD HH:MM:SS"
    run_time_str = now_utc.strftime("%Y-%m-%d %H:%M:%S")

    # 3) Write to cells
    metadata_ws.update_cell(2, 1, run_time_str)  # store UTC time in A2
    metadata_ws.update_cell(2, 2, summary_text)  # store summary in B2


def format_utc_as_local(utc_dt, tz_name="Australia/Sydney"):
    """
    Converts a UTC datetime to a chosen local timezone and returns a string.
    """
    if utc_dt is None:
        return "No previous run recorded"
    local_tz = pytz.timezone(tz_name)
    local_dt = utc_dt.astimezone(local_tz)
    return local_dt.strftime("%Y-%m-%d %H:%M:%S")


#
# 5) COOLDOWN-AWARE FUNCTION - NOW USING UTC
#
def run_all_cooldown(sheet_obj, cooldown_hours=3):
    """
    Checks if enough time has passed since last run (X hours) using UTC logic.
    If yes, run data retrieval + summarization, store new summary/time (UTC).
    If no, show the existing summary.
    """

    # Current time in UTC
    now_utc = dt.datetime.utcnow()

    # Read last-run UTC from sheet
    last_run_utc, last_summary = get_last_run_info(sheet_obj)

    if last_run_utc is not None:
        elapsed_hours = (now_utc - last_run_utc).total_seconds() / 3600.0
    else:
        # If never run, force it
        elapsed_hours = 9999

    if elapsed_hours < cooldown_hours:
        # Too soon -> use existing summary
        st.write(f"**Briefs were last run at {format_utc_as_local(last_run_utc)} local time.**")
        remain = cooldown_hours - elapsed_hours
        st.write(f"You can run again in about **{remain:.1f}** hour(s).")
        st.write("Here is the existing summary from that run:")
        return last_summary

    else:
        # Enough time -> run the pipeline
        st.write("Step 1: Fetching and storing data...")
        retrieve_and_store_data()

        st.write("Step 2: Generating summary...")
        summary_text = generate_summary()

        # Store new run time (UTC) + summary
        set_last_run_info(sheet_obj, summary_text)
        return summary_text


#
# 6) MAIN STREAMLIT APP LOGIC
#
def main():
    st.title("Foolish Financial Briefings - UTC Storage, Local Display")
    st.write(
        "Click the button below to start. Our AI will scrape what's making the "
        "news in the world of investing today, then create 5 briefs that "
        "writers can use as inspiration for their article ideas."
    )

    if st.button("Get Your Briefs!"):
        # Use the 3-hour cooldown approach
        summary = run_all_cooldown(sheet, cooldown_hours=3)

        st.success("Process complete!")
        st.subheader("AI-Generated Summary:")
        st.write(summary)


if __name__ == "__main__":
    main()
