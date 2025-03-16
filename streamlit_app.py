import streamlit as st

# Basic page config
st.set_page_config(
    page_title="Burgo's Briefing App",
    page_icon="🌟",
    layout="centered"
)

# --- BRAND STYLING ---

# We'll inject a block of CSS that:
# 1) Imports Google Fonts (Roboto + Oswald).
# 2) Defines brand color variables.
# 3) Applies brand fonts and colors throughout the UI.

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

/* Override the default font to Roboto for nearly all text */
html, body, [class*="css"]  {
  font-family: 'Roboto', sans-serif;
  color: var(--fool-midgray);  /* Set default text color to mid-gray (#53565a) */
  background-color: #ffffff;   /* White background */
}

/* Streamlit's main title or h1 classes */
h1, .stTitle {
  font-family: 'Oswald', sans-serif; /* Use Oswald for main headings */
  color: var(--fool-red);            /* Red headings */
  font-weight: 700;
  margin-bottom: 0.5rem;
}

/* Streamlit's subheader or h2 classes, if you want them styled similarly */
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

/* Style st.success messages to use the brand green as well */
.stAlert > div[role="alert"] {
  background-color: #e3f6d8 !important; /* Light green background for success messages */
  border-left: 0.25rem solid var(--fool-green) !important;
  color: var(--fool-midgray);
}

</style>
"""

# Inject the CSS block
st.markdown(BRAND_CSS, unsafe_allow_html=True)

# --- IMPORT YOUR PY SCRIPTS ---

from data_retrieval_storage_news_engine import main as retrieve_and_store_data
from step2_summarisation_with_easier_reading import generate_summary


def run_all():
    """
    This function:
    1. Fetches data from the external sources and stores them in Google Sheets.
    2. Summarizes that data using OpenAI.
    3. Returns the summary string so we can display it.
    """
    st.write("Step 1: Fetching and storing data...")
    retrieve_and_store_data()  # from data_retrieval_storage_news_engine

    st.write("Step 2: Generating summary...")
    summary_text = generate_summary()  # from step2_summarisation_with_easier_reading

    return summary_text


def main():
    st.title("Foolish Financial Briefings - Based on Trending News")
    st.write(
        "Click the button below to start. Our AI will scrape what's making the "
        "news in the world of investing today, and then create 5 briefs that "
        "writers can use as inspiration for their article ideas."
    )

    if st.button("Get Your Briefs!"):
        summary = run_all()
        st.success("All steps completed successfully!")

        # Now show the summary in the app:
        st.subheader("AI-Generated Summary:")
        st.write(summary)


if __name__ == "__main__":
    main()
