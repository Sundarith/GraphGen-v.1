# UCKG Custom Generator Plugin Documentation

## Why did we create a custom Generator Plugin?
In the `graphgen/models/generator/` directory, you will notice a custom file named `multi_hop_generator_uckg.py`. 

We created this plugin to enforce strict, Chain-of-Thought (CoT) reasoning for our Cybersecurity dataset without permanently overwriting or destroying the original GraphGen `multi_hop` generator.

### 1. The Custom Prompt (`multi_hop_generation_uckg.py`)
The original GraphGen prompt (`templates/generation/multi_hop_generation.py`) was too generic. It asked for a multi-hop question, but provided a simplistic example (Apple -> Fruit -> Vitamin C) which resulted in the LLM generating single-word answers instead of logical essays.

We created a custom template that enforces:
1. A **"Strict Professor / Cybersecurity Analyst"** persona.
2. A mandate to write highly detailed, paragraph-length answers.
3. A strict requirement to use transition words (**"First...", "Because of this...", "Therefore..."**) to prove causal relationships.

### 2. The Custom Python Class (`multi_hop_generator_uckg.py`)
This Python file is structurally **100% identical** to the original `multi_hop_generator.py`, with only two necessary modifications to make the plugin system work:
1. **The Import:** It imports our custom text prompt instead of the original prompt.
2. **The Registry:** It uses the `@GeneratorRegistry.register("multi_hop_uckg")` decorator (and imports `GeneratorRegistry`). This cleanly injects our custom pipeline into the GraphGen engine, allowing us to seamlessly select it in the YAML configuration (`method: multi_hop_uckg`) without breaking native code.