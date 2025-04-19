import os
import json
import re
import sys
import io
import contextlib
import warnings
from typing import Optional, List, Any, Tuple
from PIL import Image
import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from together import Together
from e2b_code_interpreter import Sandbox
from datetime import datetime
from pathlib import Path

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
pattern = re.compile(r"```python\n(.*?)\n```", re.DOTALL)

def code_interpret(e2b_code_interpreter: Sandbox, code: str) -> Optional[List[Any]]:
    with st.spinner('Executing code in E2B sandbox...'):
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                exec = e2b_code_interpreter.run_code(code)
        if stderr_capture.getvalue():
            print("[Code Interpreter Warnings/Errors]", file=sys.stderr)
            print(stderr_capture.getvalue(), file=sys.stderr)
        if stdout_capture.getvalue():
            print("[Code Interpreter Output]", file=sys.stdout)
            print(stdout_capture.getvalue(), file=sys.stdout)
        if exec.error:
            print(f"[Code Interpreter ERROR] {exec.error}", file=sys.stderr)
            return None
        return exec.results

def match_code_blocks(llm_response: str) -> str:
    match = pattern.search(llm_response)
    if match:
        code = match.group(1)
        return code
    return ""

def chat_with_llm(e2b_code_interpreter: Sandbox, user_message: str, dataset_path: str) -> Tuple[Optional[List[Any]], str]:
    system_prompt = f"""You're a Python data scientist and data visualization expert. You are given a dataset at path '{dataset_path}' and also the user's query.
You need to analyze the dataset and answer the user's query with a response and you run Python code to solve them.
IMPORTANT: Always use the dataset path variable '{dataset_path}' in your code when reading the CSV file."""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]
    with st.spinner('Getting response from Together AI LLM model...'):
        client = Together(api_key=st.session_state.together_api_key)
        response = client.chat.completions.create(
            model=st.session_state.model_name,
            messages=messages,
        )
        response_message = response.choices[0].message
        python_code = match_code_blocks(response_message.content)
        if python_code:
            code_interpreter_results = code_interpret(e2b_code_interpreter, python_code)
            return code_interpreter_results, response_message.content
        else:
            st.warning("Failed to match any Python code in model's response.")
            return None, response_message.content

def main():
    st.title("AI Data Visualization Agent 📊")
    st.write("Ask questions about your pre-cleaned wedding venue dataset!")

    if 'together_api_key' not in st.session_state:
        st.session_state.together_api_key = ''
    if 'e2b_api_key' not in st.session_state:
        st.session_state.e2b_api_key = ''
    if 'model_name' not in st.session_state:
        st.session_state.model_name = ''

    with st.sidebar:
        st.header("API Keys and Model Configuration")
        st.session_state.together_api_key = st.sidebar.text_input("Together API key", type="password")
        st.sidebar.markdown("[Get Together AI API Key](https://api.together.ai/signin)")
        st.session_state.e2b_api_key = st.sidebar.text_input("E2B API key", type="password")
        st.sidebar.markdown("[Get E2B API Key](https://e2b.dev/docs/legacy/getting-started/api-key)")
        model_options = {
            "Meta-Llama 3.1 405B": "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
            "DeepSeek V3": "deepseek-ai/DeepSeek-V3",
            "Qwen 2.5 7B": "Qwen/Qwen2.5-7B-Instruct-Turbo",
            "Meta-Llama 3.3 70B": "meta-llama/Llama-3.3-70B-Instruct-Turbo"
        }
        st.session_state.model_name = st.selectbox("Select Model", list(model_options.keys()), index=0)
        st.session_state.model_name = model_options[st.session_state.model_name]

    dataset_path = Path(__file__).resolve().parent.parent / "data" / "processed" / "cleaned_venues.csv"
    df = pd.read_csv(dataset_path)

    st.write("Dataset:")
    show_full = st.checkbox("Show full dataset")
    st.dataframe(df if show_full else df.head())

    query = st.text_area("What would you like to know about your data?",
                         "Can you compare the average cost for two people between different categories?")

    if st.button("Analyze"):
        if not st.session_state.together_api_key or not st.session_state.e2b_api_key:
            st.error("Please enter both API keys in the sidebar.")
        else:
            with Sandbox(api_key=st.session_state.e2b_api_key) as code_interpreter:
                with open(dataset_path, "rb") as f:
                    code_interpreter.files.write("cleaned_venues.csv", f.read())
                code_results, llm_response = chat_with_llm(code_interpreter, query, "cleaned_venues.csv")

                st.write("AI Response:")
                st.write(llm_response)

                if code_results:
                    for i, result in enumerate(code_results):
                        if hasattr(result, 'png') and result.png:
                            png_data = base64.b64decode(result.png)
                            image = Image.open(BytesIO(png_data))

                            # Display the image
                            st.image(image, caption="Generated Visualization", use_container_width=False)

                            # Download button
                            buffer = BytesIO()
                            image.save(buffer, format="PNG")
                            buffer.seek(0)

                            st.download_button(
                                label="📥 Download Chart as PNG",
                                data=buffer,
                                file_name=f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                                mime="image/png",
                                key=f"download_btn_{i}"
                            )

                        elif hasattr(result, 'figure'):
                            st.pyplot(result.figure)

                        elif hasattr(result, 'show'):
                            st.plotly_chart(result)

                        elif isinstance(result, (pd.DataFrame, pd.Series)):
                            st.dataframe(result)

                        else:
                            st.write(result)

if __name__ == "__main__":
    main()