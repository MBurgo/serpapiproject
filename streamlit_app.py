import streamlit as st
import streamlit.components.v1 as components

# Basic page config
st.set_page_config(page_title="Burgo's Briefing App", page_icon="🌟", layout="centered")

# Custom CSS
custom_css = """
<style>
.my-custom-title {
    color: #4B79A1;
    font-family: Arial, sans-serif;
    text-align: center;
    font-size: 36px;
    margin: 20px 0;
}
.my-custom-subtitle {
    color: #666666;
    text-align: center;
    margin: 5px 0 20px 0;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# We import the 'main' function from data_retrieval_storage_news_engine (which fetches & stores)
from data_retrieval_storage_news_engine import main as retrieve_and_store_data

# Instead of main, we import our new function from step2_summarisation_with_easier_reading
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
    st.write("Click the button below to start. Our AI will scrape what's making the news in the world of investing today, and then create 5 briefs that writers can use as inspiration for their article ideas.")

    if st.button("Get Your Briefs!"):
        summary = run_all()
        st.success("All steps completed successfully!")

        # Now show the summary in the app:
        st.subheader("AI-Generated Summary:")
        st.write(summary)


if __name__ == "__main__":
    main()
