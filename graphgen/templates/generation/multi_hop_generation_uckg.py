# pylint: disable=C0301
TEMPLATE_ZH: str = """请基于以下网络安全知识子图生成多跳推理问题和答案。你将获得一个知识子图，其中包含一系列实体、关系和事实。
你的任务是生成一个问答对，其中问题需要经过多次推理才能回答。问题的答案应该是从给定的知识子图中推断出来的。确保问题的难度适中，需要多步推理才能回答。

请注意下列要求：
1. 仅输出一个问答（QA）对，不得包含任何额外说明或分析
2. 不得重复答案内容或其中任何片段，不要直接复制示例问题和答案
3. 答案应准确且直接从文本中得出。确保QA对与给定文本的主题或重要细节相关。

输出格式：
<question>question_text</question>
<answer>answer_text</answer>

例如：
输入为：
--实体--
1. 蓝砸攻击 (BlueSmacking)
2. 拒绝服务 (DoS)
3. 蓝牙协议
--关系--
1. 蓝砸攻击-拒绝服务：蓝砸攻击是一种拒绝服务攻击
2. 拒绝服务-蓝牙协议：此攻击通过蓝牙协议执行

输出：
<question>蓝砸攻击通过什么协议来执行其拒绝服务目标？</question>
<answer>蓝牙协议</answer>

真实输入如下：
--实体--
{entities}
--关系--
{relationships}

输出：
"""

TEMPLATE_EN: str = """You are an expert Cybersecurity Analyst. Please generate a multi-hop reasoning question and answer based on the following cybersecurity knowledge subgraph. You will be provided with a knowledge subgraph that contains a series of entities, relations, and facts.

Your task is to generate a question-answer (QA) pair where the question requires multiple steps of reasoning to answer. The answer to the question should be inferred from the given knowledge subgraph. Ensure that the question is of moderate difficulty and requires multiple steps of reasoning to answer. 

Please note the following requirements:
1. Output only one QA pair without any additional explanations or analysis.
2. Do not repeat the content of the answer or any part of it. Do not directly copy the example question and answer.
3. The answer should be accurate and directly derived from the text. Make sure the QA pair is relevant to the main theme or important details of the given text.

For example:
Input:
--Entities--
1. BlueSmacking
2. Denial of Service (DoS)
3. Bluetooth Protocol
--Relations--
1. BlueSmacking -- Denial of Service (DoS): BlueSmacking is a type of DoS attack.
2. Denial of Service (DoS) -- Bluetooth Protocol: This specific attack leverages the Bluetooth protocol.

Output:
<question>What specific protocol must be monitored to detect the type of Denial of Service attack known as BlueSmacking?</question>
<answer>Bluetooth Protocol</answer>

Real input:
--Entities--
{entities}
--Relations--
{relationships}

Output:
"""

MULTI_HOP_GENERATION_PROMPT_UCKG = {"en": TEMPLATE_EN, "zh": TEMPLATE_ZH}
