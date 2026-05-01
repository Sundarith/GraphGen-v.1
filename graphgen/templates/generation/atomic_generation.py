# pylint: disable=C0301
TEMPLATE_EN: str = """You are an expert Cybersecurity Analyst. You are given a technical text passage containing threat intelligence. Your task is to generate a concise, factual question and answer (QA) pair based on the core cybersecurity concept within that text.

Please note the following requirements:
1. Output only one QA pair without any additional explanations or analysis.
2. Do not repeat the content of the answer or any part of it.
3. The answer should be accurate and directly derived from the text, utilizing professional cybersecurity terminology.

Output format:
<question>question_text</question>
<answer>answer_text</answer>

For example:
<question>What specific protocol is abused during a BlueSmacking Denial of Service attack?</question>
<answer>The L2CAP protocol is abused to transfer oversized packets, overwhelming the target device.</answer>

Here is the text passage you need to generate a QA pair for:
{context}

Output:
"""

TEMPLATE_ZH: str = """给定一个文本段落。你的任务是根据该文本的内容生成一个问答（QA）对。

请注意下列要求：
1. 仅输出一个问答（QA）对，不得包含任何额外说明或分析
2. 不得重复答案内容或其中任何片段
3. 答案应准确且直接从文本中得出。确保QA对与给定文本的主题或重要细节相关。

输出格式如下：
<question>question_text</question>
<answer>answer_text</answer>

例如：
<question>过表达BG1基因对谷粒大小和发育有什么影响？</question>
<answer>BG1基因的过表达显著增加了谷粒大小，表明其在谷物发育中的作用。</answer>

以下是你需要为其生成QA对的文本段落：
{context}

输出：
"""


ATOMIC_GENERATION_PROMPT = {
    "en": TEMPLATE_EN,
    "zh": TEMPLATE_ZH,
}
