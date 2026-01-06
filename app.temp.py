import streamlit as st
import streamlit.components.v1 as components
import re
from utils.llm import generate_response

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
# Custom CSS
# ---------------------------------------------------------------------
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stApp {
        background: transparent;
    }
    .content-box {
        background: white;
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        margin-bottom: 20px;
    }
    .code-header {
        color: #667eea;
        font-weight: 600;
        font-size: 20px;
        margin-bottom: 10px;
        border-bottom: 2px solid #667eea;
        padding-bottom: 5px;
    }
    .metadata-item {
        background: #f0f4ff;
        padding: 8px 15px;
        border-radius: 8px;
        margin: 5px 0;
        border-left: 4px solid #667eea;
    }
    .complexity-badge {
        display: inline-block;
        background: #e8f5e9;
        color: #2e7d32;
        padding: 5px 15px;
        border-radius: 20px;
        margin: 5px;
        font-weight: 500;
    }
    .test-case {
        background: #fff3e0;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #ff9800;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 40px;
        font-size: 16px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    }
    .mermaid-container {
        background: white;
        border-radius: 12px;
        padding: 30px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------
# Mermaid syntax validator and fixer
# ---------------------------------------------------------------------
def validate_and_fix_mermaid(mermaid_code):
    """Validates and attempts to fix common Mermaid syntax errors."""
    lines = mermaid_code.strip().split('\n')
    fixed_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Fix common syntax issues
        line = re.sub(r'([A-Za-z0-9_]+)\s*\[([^\]]+)\]', lambda m: f'{m.group(1)}["{m.group(2)}"]', line)
        line = re.sub(r'(\w+)-->(\w+)', r'\1 --> \2', line)
        line = re.sub(r'(\w+)->(\w+)', r'\1 --> \2', line)
        line = re.sub(r'\{([^\}]+)\}', r'{\1}', line)
        line = re.sub(r'-->\|([^\|]+)\|', r'--> |\1|', line)

        fixed_lines.append(line)

    return '\n'.join(fixed_lines)


# ---------------------------------------------------------------------
# Render Mermaid as HTML component
# ---------------------------------------------------------------------
def render_mermaid(mermaid_code):
    """Render Mermaid diagram using HTML component."""
    fixed_code = validate_and_fix_mermaid(mermaid_code)

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ 
                startOnLoad: true, 
                theme: 'default',
                flowchart: {{ 
                    useMaxWidth: true,
                    htmlLabels: true,
                    curve: 'basis'
                }},
                securityLevel: 'loose'
            }});
        </script>
        <style>
            body {{
                margin: 0;
                padding: 20px;
                background: white;
                font-family: Arial, sans-serif;
            }}
            .mermaid {{
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 300px;
            }}
            #error-msg {{
                display: none;
                color: #d32f2f;
                background: #ffebee;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #d32f2f;
            }}
        </style>
    </head>
    <body>
        <div id="error-msg">
            <strong>⚠️ Rendering Error</strong><br>
            The Mermaid diagram could not be rendered. Check the syntax below.
        </div>
        <div class="mermaid">
{fixed_code}
        </div>
        <script>
            window.addEventListener('load', () => {{
                setTimeout(() => {{
                    const mermaidDiv = document.querySelector('.mermaid');
                    if (mermaidDiv && !mermaidDiv.getAttribute('data-processed')) {{
                        document.getElementById('error-msg').style.display = 'block';
                    }}
                }}, 2000);
            }});
        </script>
    </body>
    </html>
    """

    components.html(html_code, height=600, scrolling=True)


# ---------------------------------------------------------------------
# Parse response sections
# ---------------------------------------------------------------------
def parse_response(response):
    """Parse the structured response into sections."""
    sections = {}

    # Extract METADATA
    metadata_match = re.search(r'===METADATA===(.*?)===END METADATA===', response, re.DOTALL)
    if metadata_match:
        metadata_text = metadata_match.group(1).strip()
        sections['metadata'] = {}
        for line in metadata_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                sections['metadata'][key.strip()] = value.strip()

    # Extract CODE
    code_match = re.search(r'===CODE===\s*```(\w+)\n(.*?)```\s*===END CODE===', response, re.DOTALL)
    if code_match:
        sections['language'] = code_match.group(1)
        sections['code'] = code_match.group(2).strip()

    # Extract VISUALIZATION
    viz_match = re.search(r'===VISUALIZATION===\s*```mermaid\n(.*?)```\s*===END VISUALIZATION===', response,
                          re.DOTALL | re.IGNORECASE)
    if viz_match:
        sections['visualization'] = viz_match.group(1).strip()
    else:
        # Fallback: try to find any mermaid code block
        viz_match = re.search(r'```mermaid\n(.*?)```', response, re.DOTALL | re.IGNORECASE)
        if viz_match:
            sections['visualization'] = viz_match.group(1).strip()

    # Extract ANNOTATED CODE
    annotated_match = re.search(r'===ANNOTATED CODE===(.*?)===END ANNOTATED===', response, re.DOTALL)
    if annotated_match:
        sections['annotated'] = annotated_match.group(1).strip()

    # Extract COMPLEXITY
    complexity_match = re.search(r'===COMPLEXITY===(.*?)===END COMPLEXITY===', response, re.DOTALL)
    if complexity_match:
        sections['complexity'] = complexity_match.group(1).strip()

    # Extract TEST CASES
    test_match = re.search(r'===TEST CASES===(.*?)===END TEST CASES===', response, re.DOTALL)
    if test_match:
        sections['test_cases'] = test_match.group(1).strip()

    return sections


# ---------------------------------------------------------------------
# Main App
# ---------------------------------------------------------------------
def main():
    # Sidebar
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
        st.markdown("### About")
        st.info("AI-powered code generator with visual flow diagrams using Mistral 7B")

    # Main content
    st.title("🎨 AI Code Visualizer")
    st.markdown("### Generate code with visual flow diagrams")

    # Input section
    user_prompt = st.text_area(
        "Enter your code request:",
        placeholder="e.g., Write a function to find the maximum subarray sum using Kadane's algorithm",
        height=100
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_btn = st.button("🚀 Generate Code", use_container_width=True)

    # Generate and display response
    if generate_btn and user_prompt:
        with st.spinner("🔄 Generating code and visualization..."):
            # Build prompt
            prompt = f"""
You are an expert senior software engineer, code reviewer, and teacher. Respond precisely in the format requested below.

TASK: {user_prompt}

OUTPUT FORMAT — Generate **only** the sections below in this exact order and format:

===METADATA===
LANGUAGE: <lowercase language, e.g. java, python, cpp>
FILENAME: <suggested filename with extension, e.g. MaxSubsetSum.java>
ALGORITHM: <short id, e.g. kadane | non_adjacent | sum_of_positives>
===END METADATA===

===CODE===
```<language>
<Complete runnable source code only. Include imports and a minimal main/test harness. No extra prose inside this fenced code block.>
```
===END CODE===

===VISUALIZATION===
```mermaid
flowchart TD
    Start([Start]) --> Step1[Step description]
    Step1 --> Decision{{Condition?}}
    Decision -->|Yes| Step2[Action if true]
    Decision -->|No| Step3[Action if false]
    Step2 --> End([End])
    Step3 --> End
```

CRITICAL MERMAID RULES:
1. ALWAYS start with "flowchart TD" on the first line
2. Node IDs must be alphanumeric only (no spaces, no special chars except underscore)
3. Use these shapes ONLY:
   - Start/End: ([Text])
   - Process: [Text]
   - Decision: {{Text}}
4. Arrow syntax: NodeA --> NodeB or NodeA -->|Label| NodeB
5. Every node must have a unique ID
6. All node IDs must be defined before use
7. Keep descriptions short and clear
8. NO line breaks inside node text
9. Example valid nodes:
   - Start([Begin])
   - Init[Initialize variables]
   - Check{{Is x > 0?}}
   - End([Finish])

===END VISUALIZATION===

===ANNOTATED CODE===
Provide the same code again with line numbers and a detailed step-by-step explanation of each line or logical block.
Numbered steps must reference line numbers (e.g., "line 3: initialize sum...").
No code fences here — explanation text only.
===END ANNOTATED===

===COMPLEXITY===
Time: O(...)
Space: O(...)
===END COMPLEXITY===

===TEST CASES===
List at least 3 test inputs and expected outputs, including edge cases.
===END TEST CASES===

RULES:
- The Mermaid diagram MUST be syntactically correct
- Test your Mermaid syntax mentally before outputting
- Use simple, clear node names
- Every path must lead to an end node
- Keep the diagram focused on main logic flow
"""

            # Generate response
            try:
                response = generate_response(prompt)

                # Extract second METADATA if duplicate exists
                matches = re.findall(r"(===METADATA===.*?)(?=(?:===METADATA===|$))", response, flags=re.DOTALL)
                if len(matches) > 1:
                    start_index = response.find(matches[1])
                    response = response[start_index:].strip()
                else:
                    match = re.search(r"(===METADATA===.*)", response, flags=re.DOTALL)
                    if match:
                        response = match.group(1).strip()

                # Store response in session state for debugging
                st.session_state['last_response'] = response

                # Parse response
                sections = parse_response(response)

                # Display sections based on user preferences
                if show_metadata and 'metadata' in sections:
                    st.markdown("## 📋 Metadata")
                    cols = st.columns(3)
                    metadata = sections['metadata']
                    if 'LANGUAGE' in metadata:
                        cols[0].markdown(f"**Language:** `{metadata['LANGUAGE']}`")
                    if 'FILENAME' in metadata:
                        cols[1].markdown(f"**Filename:** `{metadata['FILENAME']}`")
                    if 'ALGORITHM' in metadata:
                        cols[2].markdown(f"**Algorithm:** `{metadata['ALGORITHM']}`")
                    st.markdown("---")

                if show_viz and 'visualization' in sections:
                    st.markdown("## 🎨 Flow Visualization")

                    # Render the Mermaid diagram
                    viz_code = sections['visualization']

                    # Create tabs
                    tab1, tab2 = st.tabs(["📊 Diagram", "🔧 Mermaid Code"])

                    with tab1:
                        try:
                            # Render using HTML component
                            render_mermaid(viz_code)
                        except Exception as e:
                            st.error(f"Error rendering diagram: {e}")
                            st.code(viz_code, language="text")

                    with tab2:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Original**")
                            st.code(viz_code, language="text")
                        with col2:
                            st.markdown("**Fixed**")
                            fixed_viz = validate_and_fix_mermaid(viz_code)
                            st.code(fixed_viz, language="text")

                    st.markdown("---")
                else:
                    if show_viz:
                        st.warning("⚠️ No visualization found in the response")

                if show_code and 'code' in sections:
                    st.markdown("## 💻 Generated Code")
                    lang = sections.get('language', 'python')

                    # Code display with copy button
                    st.code(sections['code'], language=lang)

                    # Download code button
                    filename = sections.get('metadata', {}).get('FILENAME', 'code.txt')
                    st.download_button(
                        label="📄 Download Code",
                        data=sections['code'],
                        file_name=filename,
                        mime="text/plain",
                        key="download_code"
                    )
                    st.markdown("---")

                if show_annotated and 'annotated' in sections:
                    st.markdown("## 📝 Step-by-Step Code Explanation")

                    # Create a nice styled container for explanation
                    with st.container():
                        st.markdown("""
                        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 4px solid #667eea;">
                        """, unsafe_allow_html=True)

                        # Parse and display annotated code with better formatting
                        annotated_text = sections['annotated']

                        # Split into lines and format
                        lines = annotated_text.split('\n')
                        for line in lines:
                            if line.strip():
                                # Check if it's a line reference (e.g., "line 1:" or "1.")
                                if re.match(r'^\s*(line\s+\d+|lines?\s+\d+-\d+|\d+\.)', line, re.IGNORECASE):
                                    st.markdown(f"**{line.strip()}**")
                                else:
                                    st.markdown(line.strip())

                        st.markdown("</div>", unsafe_allow_html=True)
                    st.markdown("---")

                if show_complexity and 'complexity' in sections:
                    st.markdown("## ⚡ Complexity Analysis")

                    # Create styled complexity badges
                    complexity_text = sections['complexity'].strip()

                    col1, col2 = st.columns(2)

                    # Extract time and space complexity
                    time_match = re.search(r'Time:\s*O\((.*?)\)', complexity_text, re.IGNORECASE)
                    space_match = re.search(r'Space:\s*O\((.*?)\)', complexity_text, re.IGNORECASE)

                    with col1:
                        if time_match:
                            time_complexity = time_match.group(1)
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                        padding: 20px; border-radius: 12px; text-align: center; color: white;">
                                <h3 style="margin: 0; color: white;">⏱️ Time Complexity</h3>
                                <h2 style="margin: 10px 0; color: white;">O({time_complexity})</h2>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.info("Time complexity not specified")

                    with col2:
                        if space_match:
                            space_complexity = space_match.group(1)
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                                        padding: 20px; border-radius: 12px; text-align: center; color: white;">
                                <h3 style="margin: 0; color: white;">💾 Space Complexity</h3>
                                <h2 style="margin: 10px 0; color: white;">O({space_complexity})</h2>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.info("Space complexity not specified")

                    st.markdown("<br>", unsafe_allow_html=True)

                    # Show full complexity text if there's additional info
                    if complexity_text:
                        with st.expander("📊 Detailed Complexity Analysis"):
                            st.markdown(complexity_text)

                    st.markdown("---")

                if show_tests and 'test_cases' in sections:
                    st.markdown("## 🧪 Test Cases")

                    test_cases_text = sections['test_cases'].strip()

                    # Try to parse individual test cases
                    # Look for patterns like "Test Case 1:", "Input:", "Output:", etc.
                    test_sections = re.split(r'(Test Case \d+|Case \d+|Example \d+)', test_cases_text,
                                             flags=re.IGNORECASE)

                    if len(test_sections) > 1:
                        # We found structured test cases
                        for i in range(1, len(test_sections), 2):
                            if i + 1 < len(test_sections):
                                test_header = test_sections[i]
                                test_content = test_sections[i + 1].strip()

                                # Determine test case type/color
                                if 'edge' in test_content.lower() or 'edge' in test_header.lower():
                                    color = "#ff9800"
                                    icon = "🔶"
                                    badge = "Edge Case"
                                elif 'normal' in test_content.lower() or 'basic' in test_content.lower():
                                    color = "#4caf50"
                                    icon = "✅"
                                    badge = "Normal Case"
                                else:
                                    color = "#2196f3"
                                    icon = "🔵"
                                    badge = "Test Case"

                                st.markdown(f"""
                                <div style="background: white; border-left: 4px solid {color}; 
                                            padding: 20px; border-radius: 8px; margin: 15px 0; 
                                            box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                                    <div style="display: flex; align-items: center; margin-bottom: 10px;">
                                        <span style="font-size: 24px; margin-right: 10px;">{icon}</span>
                                        <h4 style="margin: 0; color: #333;">{test_header}</h4>
                                        <span style="margin-left: auto; background: {color}; color: white; 
                                                     padding: 4px 12px; border-radius: 12px; font-size: 12px;">
                                            {badge}
                                        </span>
                                    </div>
                                    <div style="color: #555; line-height: 1.6;">
                                        {test_content.replace(chr(10), '<br>')}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        # Fallback: display as-is with nice formatting
                        st.markdown(f"""
                        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; 
                                    border-left: 4px solid #2196f3;">
                            {test_cases_text.replace(chr(10), '<br>')}
                        </div>
                        """, unsafe_allow_html=True)

                # Success message
                st.success("✅ Code generation completed successfully!")

                # Download button for full response
                st.download_button(
                    label="📥 Download Full Response",
                    data=response,
                    file_name="code_response.txt",
                    mime="text/plain"
                )

                # Debug expander
                with st.expander("🔍 Debug Info"):
                    st.write("**Found sections:**", list(sections.keys()))
                    if 'visualization' in sections:
                        st.write("**Visualization length:**", len(sections['visualization']))
                        st.code(sections['visualization'][:500], language="text")

            except Exception as e:
                st.error(f"❌ Error generating code: {str(e)}")
                st.exception(e)

    elif generate_btn:
        st.warning("⚠️ Please enter a code request first!")


if __name__ == "__main__":
    main()