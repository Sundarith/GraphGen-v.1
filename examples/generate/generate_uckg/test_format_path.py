import json
import os

# Try to find the file in the new pipelines location first, fallback to the integration folder
DATA_FILE = os.path.expanduser("~/Desktop/UCKG/fine-tuning/pipelines/clean_data.jsonl")
if not os.path.exists(DATA_FILE):
    DATA_FILE = "UCKG_Integration/data-generation/clean_data.jsonl"

def format_list(item_list):
    """Helper to format lists into bullet points or return empty string."""
    if not item_list:
        return "None specified."
    if isinstance(item_list, list):
        # Using chr(10) to safely insert a newline character without causing syntax errors in the write_file tool
        nl = chr(10)
        return nl.join(f"- {item}" for item in item_list)
    return str(item_list)

def test_format_single_path():
    if not os.path.exists(DATA_FILE):
        print(f"Error: {DATA_FILE} not found. Please ensure it exists.")
        return

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        first_line = f.readline()
        if not first_line:
            print("File is empty.")
            return
            
        row = json.loads(first_line)
        
        c = row.get("c", {})
        a = row.get("a", {})
        m = row.get("m", {})

        c_name = c.get("ucoexCAPEC_name", c.get("Name", "Unknown Attack"))
        a_name = a.get("ucoexNAME", a.get("Name", "Unknown Category"))
        m_name = m.get("ucoexNAME", m.get("Name", "Unknown Mitigation"))

        c_desc = c.get("ucoexDescription", c.get("Description", "No description."))
        a_desc = a.get("ucoexDESCRIPTION", a.get("Description", "No description."))
        m_desc = m.get("ucoexDESCRIPTION", m.get("Description", "No description."))

        c_prereqs = format_list(c.get("ucoexPrerequisites", []))
        c_tech = format_list(c.get("ucoexExecutionFlowTechnique", c.get("Technique", [])))
        c_cons = format_list(c.get("ucoexConsequences", []))

        # Using a safer formatting approach to avoid multiline string issues
        nl = chr(10)
        paragraph = (
            f"=================================================={nl}"
            f"INCIDENT REPORT TEST (1 PATH){nl}"
            f"=================================================={nl}{nl}"
            f"Incident Report: {c_name}{nl}{nl}"
            f"Attack Summary:{nl}{c_desc}{nl}{nl}"
            f"Prerequisites:{nl}{c_prereqs}{nl}{nl}"
            f"Execution Steps:{nl}{c_tech}{nl}{nl}"
            f"Consequences:{nl}{c_cons}{nl}{nl}"
            f"Broader Category:{nl}"
            f"This specific attack is a form of **{a_name}**, which is defined as: {a_desc}{nl}{nl}"
            f"Defense Strategy:{nl}"
            f"To mitigate this attack and related {a_name} threats, defenders should implement **{m_name}**. "
            f"This strategy involves: {m_desc}{nl}"
            f"=================================================="
        )

        print(paragraph)

if __name__ == "__main__":
    test_format_single_path()
