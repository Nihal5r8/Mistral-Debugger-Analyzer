import os
import re
from utils.llm import generate_response
from utils.visualizer import render_graphviz


# ---------------------------------------------------------------------
# Mermaid syntax validator and fixer
# ---------------------------------------------------------------------
def validate_and_fix_mermaid(mermaid_code):
    """
    Validates and attempts to fix common Mermaid syntax errors.
    """
    lines = mermaid_code.strip().split('\n')
    fixed_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Fix common syntax issues
        # 1. Remove invalid characters from node IDs
        line = re.sub(r'([A-Za-z0-9_]+)\s*\[([^\]]+)\]', lambda m: f'{m.group(1)}["{m.group(2)}"]', line)

        # 2. Fix arrow syntax (ensure spaces around arrows)
        line = re.sub(r'(\w+)-->(\w+)', r'\1 --> \2', line)
        line = re.sub(r'(\w+)->(\w+)', r'\1 --> \2', line)

        # 3. Fix decision nodes (ensure proper syntax)
        line = re.sub(r'\{([^\}]+)\}', r'{\1}', line)

        # 4. Fix labels on arrows
        line = re.sub(r'-->\|([^\|]+)\|', r'--> |\1|', line)

        fixed_lines.append(line)

    return '\n    '.join(fixed_lines)


# ---------------------------------------------------------------------
# Render Mermaid diagrams as HTML with fallback
# ---------------------------------------------------------------------
def render_mermaid_html(mermaid_code, output_path="outputs/viz.html"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Try to fix common syntax errors
    fixed_mermaid = validate_and_fix_mermaid(mermaid_code)

    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mermaid Diagram</title>
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

        // Error handling
        window.addEventListener('load', () => {{
            setTimeout(() => {{
                const errorDiv = document.querySelector('.mermaid-error');
                const mermaidDiv = document.querySelector('.mermaid');
                if (mermaidDiv && mermaidDiv.getAttribute('data-processed') !== 'true') {{
                    errorDiv.style.display = 'block';
                    console.error('Mermaid rendering failed');
                }}
            }}, 2000);
        }});
    </script>
    <style>
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px; 
            margin: 0;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h2 {{ 
            color: #333; 
            margin-top: 0;
            font-size: 28px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        .mermaid {{ 
            background: #fafafa; 
            border-radius: 12px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
            padding: 20px;
            margin: 20px 0;
            min-height: 200px;
        }}
        .mermaid-error {{
            display: none;
            background: #fee;
            border: 2px solid #fcc;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            color: #c33;
        }}
        .original-code {{
            background: #f4f4f4;
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
            overflow-x: auto;
        }}
        .original-code h3 {{
            margin-top: 0;
            color: #555;
        }}
        .original-code pre {{
            margin: 0;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2>🎨 Code Flow Visualization</h2>

        <div class="mermaid-error">
            <strong>⚠️ Mermaid Rendering Error</strong>
            <p>The diagram could not be rendered. This might be due to syntax errors in the generated Mermaid code.</p>
            <p>Check the original code section below for details.</p>
        </div>

        <div class="mermaid">
{fixed_mermaid}
        </div>

        <div class="original-code">
            <h3>Original Mermaid Code</h3>
            <pre><code>{mermaid_code}</code></pre>
        </div>

        <div class="original-code">
            <h3>Fixed Mermaid Code</h3>
            <pre><code>{fixed_mermaid}</code></pre>
        </div>
    </div>
</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_template)
    print(f"✅ Mermaid diagram saved to {output_path}")


# ---------------------------------------------------------------------
# Enhanced prompt with strict Mermaid syntax guidelines
# ---------------------------------------------------------------------
user_prompt = input("Enter your code request: ")

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

# ---------------------------------------------------------------------
# Run the model
# ---------------------------------------------------------------------
response = generate_response(prompt)

# ---------------------------------------------------------------------
# Extract second METADATA and everything after
# ---------------------------------------------------------------------
matches = re.findall(r"(===METADATA===.*?)(?=(?:===METADATA===|$))", response, flags=re.DOTALL)
if len(matches) > 1:
    start_index = response.find(matches[1])
    response = response[start_index:].strip()
else:
    match = re.search(r"(===METADATA===.*)", response, flags=re.DOTALL)
    if match:
        response = match.group(1).strip()

# ---------------------------------------------------------------------
# Extract visualization (Mermaid or Graphviz)
# ---------------------------------------------------------------------
viz_match = re.search(r"```(mermaid|dot)\n(.*?)```", response, flags=re.DOTALL | re.IGNORECASE)
if viz_match:
    viz_type = viz_match.group(1).lower()
    viz_data = viz_match.group(2).strip()

    if viz_type == "mermaid":
        print(f"📊 Found Mermaid diagram ({len(viz_data)} chars)")
        # Render Mermaid HTML with validation
        render_mermaid_html(viz_data)
    elif viz_type == "dot":
        print("📊 Found Graphviz diagram")
        render_graphviz(viz_data)
    else:
        print("⚠️ Visualization format not recognized.")
else:
    print("⚠️ No valid visualization found in model output.")
    # Try to extract any code block that might be mermaid
    fallback_match = re.search(r"```\n(flowchart.*?)```", response, flags=re.DOTALL | re.IGNORECASE)
    if fallback_match:
        print("🔄 Found potential Mermaid code without language tag, attempting to render...")
        render_mermaid_html(fallback_match.group(1).strip())

# ---------------------------------------------------------------------
# Print final clean output
# ---------------------------------------------------------------------
print("\n=== MODEL RESPONSE ===\n")
print(response)