# pylint: disable=C0301
TEMPLATE_EN: str = """You are an expert Cybersecurity Analyst. You are given a cybersecurity knowledge subgraph containing threat intelligence entities and their relationships. Your task is to generate a multi-hop reasoning question and answer that requires connecting information across the provided entities and relationships.

Please note the following requirements:
1. Output only one QA pair without any additional explanations or analysis.
2. Do not repeat the content of the answer or any part of it. Do not directly copy the example question and answer.
3. The question must require at least two reasoning steps to answer — it should not be answerable from a single entity alone.
4. Use professional cybersecurity terminology accurately in both the question and the answer.

For example:
Input:
--Entities--
1. BlueSmacking: A Denial of Service attack that exploits the Bluetooth L2CAP protocol by sending oversized packets.
2. T1498.001: Network Denial of Service via Direct Network Flood — a MITRE ATT&CK technique.
--Relations--
1. BlueSmacking -- T1498.001: BlueSmacking is classified under this ATT&CK sub-technique.

Output:
<question>Given that BlueSmacking exploits the L2CAP protocol to overwhelm a target, which MITRE ATT&CK sub-technique does this attack fall under?</question>
<answer>BlueSmacking is classified under T1498.001 — Network Denial of Service via Direct Network Flood — because it uses Bluetooth L2CAP packet flooding to saturate and disable the target device.</answer>

Real input:
--Entities--
{entities}
--Relations--
{relationships}

Output:
"""

MULTI_HOP_CYBER_GENERATION_PROMPT = {"en": TEMPLATE_EN}
