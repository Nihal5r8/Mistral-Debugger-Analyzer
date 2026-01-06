import streamlit as st
import re

# --- IMPORT UTILITIES ---
from utils.llm import generate_response
from utils.parser import parse_response
from utils.visualizer import render_mermaid, validate_and_fix_mermaid

# ---------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="AI Code Visualizer",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------------------
# Custom CSS (Enhanced Design)
# ---------------------------------------------------------------------
st.markdown("""
<style>
    .main { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .stApp { background: transparent; }
    .content-box { background: white; border-radius: 16px; padding: 25px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); margin-bottom: 20px; }
    .mermaid-box { background: #f9fafb; border-radius: 16px; padding: 25px; box-shadow: 0 8px 20px rgba(0,0,0,0.1); margin: 20px 0; }
    .section-title { font-size: 22px; font-weight: 700; color: #333; margin-bottom: 15px; }
    .stButton>button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 25px; padding: 12px 40px; font-size: 16px; font-weight: 600; transition: all 0.3s ease; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4); }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------
# Main App
# ---------------------------------------------------------------------
def main():
    with st.sidebar:
        st.title("⚙️ Settings")
        st.markdown("---")
        show_metadata = st.checkbox("Show Metadata", value=True)
        show_viz = st.checkbox("Show Visualization", value=True)
        show_code = st.checkbox("Show Code", value=True)
        show_annotated = st.checkbox("Show Annotated Code", value=True)
        show_complexity = st.checkbox("Show Complexity", value=True)
        show_tests = st.checkbox("Show Test Cases", value=True)
        st.markdown("---")
        st.info("AI-powered code generator with visual flow diagrams using Mistral 7B")

    st.title("🎨 AI Code Visualizer")
    st.markdown("### Generate code with visual flow diagrams")

    user_prompt = st.text_area(
        "Enter your code request:",
        placeholder="e.g., Write a function to find the maximum subarray sum using Kadane's algorithm",
        height=100
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Generate Code", use_container_width=True) and user_prompt:
            with st.spinner("🔄 Generating code and visualization using local Mistral 7B..."):
                try:
                    response = generate_response(f"""
Generate the mermaid syntax according to the rules
You are an expert software engineer. Follow this format strictly:

===METADATA===
LANGUAGE: <language>
FILENAME: <filename>
ALGORITHM: <algorithm>
===END METADATA===

===CODE===
```<language>
<code>
```
===END CODE===

===VISUALIZATION===
```mermaid
flowchart TD
Start([Start]) --> Step1[Do something]
Step1 --> End([End])
```
===END VISUALIZATION===

===ANNOTATED CODE===
Detailed line-by-line explanation.
===END ANNOTATED===

===COMPLEXITY===
Time: O(n)
Space: O(1)
===END COMPLEXITY===

===TEST CASES===
Test 1: 
input:
output:
===END TEST CASES===
TASK: {user_prompt}
""")

                    st.session_state['last_response'] = response
                    sections = parse_response(response)
                    # st.write("🔍 Parsed sections:", list(sections.keys()))

                    # --- METADATA ---
                    if show_metadata and sections.get('metadata'):
                        with st.container():
                            st.markdown('<div class="content-box">', unsafe_allow_html=True)
                            st.subheader("📋 Metadata")
                            md = sections['metadata']
                            st.markdown(f"**Language:** `{md.get('LANGUAGE','N/A')}`  ")
                            st.markdown(f"**Filename:** `{md.get('FILENAME','N/A')}`  ")
                            st.markdown(f"**Algorithm:** `{md.get('ALGORITHM','N/A')}`")
                            st.markdown('</div>', unsafe_allow_html=True)

                    # --- CODE ---
                    if show_code and sections.get('code'):
                        with st.container():
                            st.markdown('<div class="content-box">', unsafe_allow_html=True)
                            st.subheader("💻 Generated Code")
                            st.code(sections['code'], language=sections.get('language','python'))
                            st.markdown('</div>', unsafe_allow_html=True)

                    # --- VISUALIZATION ---
                    if show_viz and sections.get('visualization'):
                        with st.container():
                            st.markdown('<div class="mermaid-box">', unsafe_allow_html=True)
                            st.subheader("🎨 Flow Visualization")
                            try:
                                render_mermaid(sections['visualization'])
                            except Exception as e:
                                st.error(f"Mermaid render error: {e}")
                                st.code(sections['visualization'], language='text')
                            st.markdown('</div>', unsafe_allow_html=True)

                    # --- ANNOTATED CODE ---
                    if show_annotated and sections.get('annotated'):
                        with st.container():
                            st.markdown('<div class="content-box">', unsafe_allow_html=True)
                            st.subheader("📝 Step-by-Step Explanation")
                            for line in sections['annotated'].split('\n'):
                                if re.match(r'^\s*(line\s+\d+|lines?\s+\d+-\d+|\d+\.)', line, re.IGNORECASE):
                                    st.markdown(f"**{line.strip()}**")
                                else:
                                    st.markdown(line.strip())
                            st.markdown('</div>', unsafe_allow_html=True)

                    # --- COMPLEXITY ---
                    if show_complexity and sections.get('complexity'):
                        with st.container():
                            st.markdown('<div class="content-box">', unsafe_allow_html=True)
                            st.subheader("⚡ Complexity Analysis")
                            st.markdown(sections['complexity'])
                            st.markdown('</div>', unsafe_allow_html=True)

                    # --- TEST CASES ---
                    if show_tests and sections.get('test_cases'):
                        with st.container():
                            st.markdown('<div class="content-box">', unsafe_allow_html=True)
                            st.subheader("🧪 Test Cases")
                            st.markdown(sections['test_cases'].replace('\n','<br>'), unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)

                    st.download_button("📥 Download Full Response", response, file_name="response.txt")
                    st.success("✅ Code generation completed!")

                except Exception as e:
                    st.error(f"❌ Error generating or parsing: {e}")

        elif user_prompt == "":
            st.warning("⚠️ Please enter a code request first!")

if __name__ == "__main__":
    main()
