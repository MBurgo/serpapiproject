import streamlit as st

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
    st.title("Financial Data Retrieval & Summaries")
    st.write("Click the button below to fetch/store data and generate a summary in one step.")

    if st.button("Run All Steps"):
        summary = run_all()
        st.success("All steps completed successfully!")

        # Now show the summary in the app:
        st.subheader("AI-Generated Summary:")
        st.write(summary)


if __name__ == "__main__":
    main()
