# pylint: disable=C0301
TEMPLATE_EN: str = """You are an NLP expert, skilled at analyzing text to extract named entities and their relationships for a Cybersecurity Knowledge Graph.

-Goal-
Given a text document containing cybersecurity incident reports or threat intelligence, identify all entities and all relationships among them.
Use English as output language.

-Steps-
1. Identify all entities. For each identified entity, extract the following information:
- entity_name: Name of the entity, use same language as input text. If English, capitalized the name.
- entity_type: One of the following types: [{entity_types}]
- entity_summary: Comprehensive summary of the entity's attributes and activities
Format each entity as ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_summary>)

2. From the entities identified in step 1, identify all pairs of (source_entity, target_entity) that are *clearly related* to each other.
For each pair of related entities, extract the following information:
- source_entity: name of the source entity, as identified in step 1
- target_entity: name of the target entity, as identified in step 1
- relationship_summary: explanation as to why you think the source entity and the target entity are related to each other
Format each relationship as ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_summary>)

3. Identify high-level key words that summarize the main concepts, themes, or topics of the entire text. These should capture the overarching ideas present in the document.
Format the content-level key words as ("content_keywords"{tuple_delimiter}<high_level_keywords>)

4. Return output in English as a single list of all the entities and relationships identified in steps 1 and 2. Use **{record_delimiter}** as the list delimiter.

5. When finished, output {completion_delimiter}

################
-Examples-
################
-Example 1-
Text:
################
Incident Report: BlueSmacking
Attack Summary: An adversary uses Bluetooth flooding to transfer large packets to Bluetooth enabled devices over the L2CAP protocol with the goal of creating a DoS. 
Tactical Mitigation: Disable Bluetooth when not being used.
################
Output:
("entity"{tuple_delimiter}"BlueSmacking"{tuple_delimiter}"attack_pattern"{tuple_delimiter}"An attack that uses Bluetooth flooding to transfer large packets over the L2CAP protocol."){record_delimiter}
("entity"{tuple_delimiter}"Bluetooth Flooding"{tuple_delimiter}"attack_pattern"{tuple_delimiter}"A technique involving the transfer of large packets to overwhelm a target."){record_delimiter}
("entity"{tuple_delimiter}"Bluetooth Enabled Devices"{tuple_delimiter}"software"{tuple_delimiter}"The target of the BlueSmacking attack."){record_delimiter}
("entity"{tuple_delimiter}"L2CAP Protocol"{tuple_delimiter}"concept"{tuple_delimiter}"The protocol abused during a BlueSmacking attack."){record_delimiter}
("entity"{tuple_delimiter}"Denial of Service (DoS)"{tuple_delimiter}"category"{tuple_delimiter}"The ultimate goal of the BlueSmacking attack."){record_delimiter}
("entity"{tuple_delimiter}"Disable Bluetooth"{tuple_delimiter}"mitigation"{tuple_delimiter}"A tactical defense strategy to stop the attack."){record_delimiter}
("relationship"{tuple_delimiter}"BlueSmacking"{tuple_delimiter}"Bluetooth Flooding"{tuple_delimiter}"BlueSmacking is executed by using Bluetooth Flooding."){record_delimiter}
("relationship"{tuple_delimiter}"BlueSmacking"{tuple_delimiter}"L2CAP Protocol"{tuple_delimiter}"The attack abuses the L2CAP protocol to transfer packets."){record_delimiter}
("relationship"{tuple_delimiter}"BlueSmacking"{tuple_delimiter}"Denial of Service (DoS)"{tuple_delimiter}"The goal of the attack is to cause a DoS."){record_delimiter}
("relationship"{tuple_delimiter}"Disable Bluetooth"{tuple_delimiter}"BlueSmacking"{tuple_delimiter}"Disabling Bluetooth mitigates the attack."){record_delimiter}
("content_keywords"{tuple_delimiter}"Bluetooth security, DoS attacks, L2CAP, mitigation"){completion_delimiter}

################
-Real Data-
################
Entity_types: {entity_types}
Text: {input_text}
################
Output:
"""

TEMPLATE_ZH: str = """(Skipped for UCKG)"""

CONTINUE_EN: str = """MANY entities and relationships were missed in the last extraction.  \
Add them below using the same format:
"""

CONTINUE_ZH: str = """(Skipped for UCKG)"""

IF_LOOP_EN: str = """It appears some entities and relationships may have still been missed.  \
Answer YES | NO if there are still entities and relationships that need to be added.
"""

IF_LOOP_ZH: str = """(Skipped for UCKG)"""

KG_EXTRACTION_PROMPT_UCKG: dict = {
    "en": {
        "TEMPLATE": TEMPLATE_EN,
        "CONTINUE": CONTINUE_EN,
        "IF_LOOP": IF_LOOP_EN,
    },
    "zh": {
        "TEMPLATE": TEMPLATE_ZH,
        "CONTINUE": CONTINUE_ZH,
        "IF_LOOP": IF_LOOP_ZH,
    },
    "FORMAT": {
        "tuple_delimiter": "<|>",
        "record_delimiter": "##",
        "completion_delimiter": "<|COMPLETE|>",
        "entity_types": "attack_pattern, category, mitigation, vulnerability, software, threat_actor, tool, concept",
    },
}
