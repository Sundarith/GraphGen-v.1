# pylint: disable=C0301
TEMPLATE_EN: str = """You are an expert Cybersecurity Analyst. Your task is to generate exactly 3 distinct Question and Answer (QA) pairs based on the technical details provided in the text.

Please note the following requirements:
1. **Output exactly 3 QA pairs.**
2. **Questions:**
   - Must be specific (e.g., ask about the mechanism, protocol, goal, or prerequisites).
   - **MUST explicitly name the attack or concept** (e.g., "What protocol does BlueSmacking use?"). Do NOT use "this attack", "the pattern", or "the text".
3. **Answers:**
   - Start by directly answering the specific question.
   - Then, **expand to include the full technical context/mechanism** provided in the source text. This ensures the answer is comprehensive and covers all details (protocols, constraints, consequences).

Output format:
<question>question_1</question>
<answer>direct_answer + full_context</answer>
<question>question_2</question>
<answer>direct_answer + full_context</answer>
<question>question_3</question>
<answer>direct_answer + full_context</answer>

Here is the text passage you need to generate QA pairs for:
{context}

Output:
"""

TEMPLATE_ZH: str = """给定一个文本段落。你的任务是根据该文本的内容生成一个问答（QA）对。

请注意下列要求：
1. 仅输出一个问答（QA）对。
2. 问题应要求对文本中的具体攻击模式或概念进行**全面描述**或**详细解释**。
3. 答案必须**极其详细**且**忠实于文本**。它应包含源文本中提到的所有技术协议、特定限制（如“近距离”）、后果和机制。不要进行总结；应包含所提供信息的全部丰富内容。

输出格式如下：
<question>question_text</question>
<answer>answer_text</answer>

例如：
<question>请详细描述BlueSmacking攻击模式，包括其技术机制和限制条件。</question>
<answer>BlueSmacking是一种攻击，攻击者利用蓝牙泛洪通过L2CAP协议向启用蓝牙的设备传输大数据包。其目标是造成拒绝服务（DoS）状态。此攻击受限于必须在目标启用蓝牙的设备近距离内进行。</answer>

以下是你需要为其生成QA对的文本段落：
{context}

输出：
"""


ATOMIC_GENERATION_PROMPT = {
    "en": TEMPLATE_EN,
    "zh": TEMPLATE_ZH,
}
