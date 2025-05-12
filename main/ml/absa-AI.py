import streamlit as st
import pandas as pd
from together import Together
from datetime import datetime
import time
import sys
from pathlib import Path
from config.keys import TOGETHER_API_KEY

# Add parent directory to path to import utils
sys.path.append(str(Path(__file__).parent.parent))

# Import file utilities
from utils.file_utils import setup_directories

def perform_sentiment_analysis(client, model_name, venue_name, reviews):
    """Use the Together AI API to perform aspect-based sentiment analysis"""
    
    # Prepare reviews for prompt context (limit to prevent token overflow)
    MAX_REVIEWS = 50
    reviews_text = "\n\n".join([f"Review {i+1}: {r}" for i, r in enumerate(reviews[:MAX_REVIEWS])])
    review_count = len(reviews)
    
    system_prompt = f"""You are an expert in aspect-based sentiment analysis for wedding venues. 
Analyze the sentiment for different aspects of the venue '{venue_name}' based on {review_count} reviews (showing first {min(MAX_REVIEWS, review_count)} below).

Identify the following aspects and analyze sentiment for each:
- Food and Catering
- Service and Staff
- Value for Money
- Location and Accessibility
- Venue Facilities and Ambiance
- Communication and Planning Process
- Flexibility
- Overall Experience

For each aspect:
1. Determine if the aspect is positive, negative, or mixed
2. Estimate a sentiment score from 1-10
3. Extract key phrases or words that indicate the sentiment
4. Provide specific insights and quotes from the reviews

Present your analysis as a structured report with sections for each aspect.
Use bullet points where appropriate for clarity.
Include a final summary with recommendations for couples considering this venue.

Reviews:
{reviews_text}

Note: These are {min(MAX_REVIEWS, review_count)} out of {review_count} total reviews. Your analysis should reflect this sample.
"""
    
    user_prompt = f"Please perform an aspect-based sentiment analysis for the wedding venue '{venue_name}'."
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    
    # Call the API
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
    )
    
    return response.choices[0].message.content

def main():
    st.title("Wedding Venue Sentiment Analysis 💒")
    
    # Setup directories with correct base path
    base_dir = Path(__file__).resolve().parent.parent  # Go up to main directory
    dirs = setup_directories(base_data_dir=base_dir / "data")
    dataset_path = dirs.processed_dir / "venue_reviews.csv"
    
    # Initialize session state with API key from config
    if 'together_api_key' not in st.session_state:
        st.session_state.together_api_key = TOGETHER_API_KEY
    if 'model_name' not in st.session_state:
        st.session_state.model_name = ''


    with st.sidebar:
        st.header("Model Configuration")
        model_options = {
            "Meta-Llama 3.1 405B": "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
            "DeepSeek V3": "deepseek-ai/DeepSeek-V3",
            "Qwen 2.5 7B": "Qwen/Qwen2.5-7B-Instruct-Turbo",
            "Meta-Llama 3.3 70B": "meta-llama/Llama-3.3-70B-Instruct-Turbo"
        }
        st.session_state.model_name = st.selectbox("Select Model", list(model_options.keys()), index=0)
        st.session_state.model_name = model_options[st.session_state.model_name]

    try:
        df = pd.read_csv(dataset_path)
        st.write("Analyze sentiment across different aspects for a specific wedding venue based on reviews.")
        
        # Dataset preview
        with st.expander("Dataset Preview"):
            st.dataframe(df)
            st.write(f"Total venues: {len(df['venue_no'].unique())}")
            st.write(f"Total reviews: {len(df)}")
        
        # Get unique venue names for the dropdown
        venue_names = sorted(df['venue_name'].unique())
        
        # Create a dropdown to select venue name
        st.subheader("Select a Venue")
        selected_venue = st.selectbox("Choose a Wedding Venue", venue_names)
        
        # Add some information about the selected venue
        if selected_venue:
            venue_info = df[df['venue_name'] == selected_venue].iloc[0]
            st.write(f"**Location:** {venue_info.get('location', 'N/A')}")
            
            # Count reviews for this venue
            venue_reviews = df[df['venue_name'] == selected_venue]
            review_count = len(venue_reviews)
            st.write(f"**Number of Reviews:** {review_count}")
            
            # Show a sample review
            with st.expander("View a sample review for this venue"):
                sample_review = venue_reviews.iloc[0]
                st.write(sample_review.get('review_text', 'No review text available'))
        
        analysis_btn = st.button("Analyze Sentiment")
        
        if analysis_btn:
            if not st.session_state.together_api_key:
                st.error("Please enter your Together API key in the sidebar.")
            else:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Update progress bar
                status_text.text("Starting analysis...")
                progress_bar.progress(10)
                time.sleep(0.5)
                
                status_text.text("Collecting venue reviews...")
                progress_bar.progress(30)
                
                # Get all reviews for the selected venue
                venue_reviews = df[df['venue_name'] == selected_venue]['review_text'].tolist()
                
                status_text.text("Performing sentiment analysis with AI...")
                progress_bar.progress(50)
                
                try:
                    # Create Together AI client
                    client = Together(api_key=st.session_state.together_api_key)
                    
                    # Get sentiment analysis from LLM
                    sentiment_analysis = perform_sentiment_analysis(
                        client, 
                        st.session_state.model_name,
                        selected_venue,
                        venue_reviews
                    )
                    
                    status_text.text("Processing results...")
                    progress_bar.progress(90)
                    time.sleep(0.5)
                    
                    # Display results
                    st.subheader("Sentiment Analysis Results")
                    st.markdown(sentiment_analysis)
                    
                    # Complete the progress bar
                    progress_bar.progress(100)
                    status_text.text("Analysis complete!")
                    
                    # Add download buttons for analysis report
                    st.subheader("Download Analysis")
                    
                    # Create a markdown report
                    report_content = f"""# Aspect-Based Sentiment Analysis for {selected_venue}

{sentiment_analysis}

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
                    
                    # Download button for the report
                    st.download_button(
                        label="📄 Download Report as Markdown",
                        data=report_content,
                        file_name=f"{selected_venue.replace(' ', '_')}_sentiment_analysis.md",
                        mime="text/markdown"
                    )
                    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    progress_bar.empty()
                    status_text.empty()
    
    except FileNotFoundError:
        st.error(f"Could not find the dataset file: {dataset_path}. Please ensure it's in the same directory as this script.")
    except Exception as e:
        st.error(f"An error occurred while loading the dataset: {str(e)}")

if __name__ == "__main__":
    main()