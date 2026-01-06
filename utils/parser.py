import re

# --- Define Strict Markers (These MUST match the prompt in app.py) ---
METADATA_START = "===METADATA==="
METADATA_END = "===END METADATA==="
CODE_START = "===CODE==="
CODE_END = "===END CODE==="
VIZ_START = "===VISUALIZATION==="
VIZ_END = "===END VISUALIZATION==="
ANNOTATED_START = "===ANNOTATED CODE==="
ANNOTATED_END = "===END ANNOTATED==="
COMPLEXITY_START = "===COMPLEXITY==="
COMPLEXITY_END = "===END COMPLEXITY==="
TEST_START = "===TEST CASES==="
TEST_END = "===END TEST CASES==="


def parse_response(response: str):
    """
    Parses the LLM's structured response into a dictionary of sections.
    Now simplified — assumes model no longer echoes the prompt,
    but still robust to accidental repetitions.
    """

    sections = {}

    # --- Step 1: Remove accidental prompt echoes (if still happen) ---
    # If the model repeated your prompt, trim before the first METADATA_START
    if response.count(METADATA_START) > 1:
        first = response.find(METADATA_START)
        second = response.find(METADATA_START, first + len(METADATA_START))
        response = response[second:].strip()

    # If somehow the model included "TASK:" or similar instruction before output,
    # this ensures we start right at the first real marker.
    first_metadata_index = response.find(METADATA_START)
    if first_metadata_index != -1:
        response = response[first_metadata_index:].strip()

    # --- Step 2: Helper function to extract text between markers ---
    def extract_section(start_marker, end_marker):
        match = re.search(
            f'{re.escape(start_marker)}(.*?){re.escape(end_marker)}',
            response,
            re.DOTALL | re.IGNORECASE
        )
        if match:
            return match.group(1).strip()
        return None

    # --- Step 3: Extract all sections ---
    sections['metadata'] = extract_section(METADATA_START, METADATA_END)
    sections['code'] = extract_section(CODE_START, CODE_END)
    sections['visualization'] = extract_section(VIZ_START, VIZ_END)
    sections['annotated'] = extract_section(ANNOTATED_START, ANNOTATED_END)
    sections['complexity'] = extract_section(COMPLEXITY_START, COMPLEXITY_END)
    sections['test_cases'] = extract_section(TEST_START, TEST_END)

    # --- Step 4: Normalize content ---
    # Metadata
    if sections['metadata']:
        metadata_dict = {}
        for line in sections['metadata'].splitlines():
            if ':' in line:
                key, value = line.split(':', 1)
                metadata_dict[key.strip().upper()] = value.strip()
        sections['metadata'] = metadata_dict
        sections['language'] = metadata_dict.get('LANGUAGE', 'python').lower()

    # Code block
    if sections['code']:
        code_match = re.search(r'```(\w+)\n(.*?)```', sections['code'], re.DOTALL)
        if code_match:
            sections['language'] = code_match.group(1).lower()
            sections['code'] = code_match.group(2).strip()
        else:
            sections['code'] = sections['code'].strip()

    # Visualization cleanup
    if sections['visualization']:
        sections['visualization'] = (
            sections['visualization']
            .replace('```mermaid', '')
            .replace('```', '')
            .strip()
        )

    return sections
