import sys
import os

# 1. Import the new custom prompt dictionary
from examples.generate.generate_uckg.kg_extraction_uckg import KG_EXTRACTION_PROMPT_UCKG

# 2. Import the original GraphGen engine's module that holds the hardcoded prompt
import graphgen.models.kg_builder.light_rag_kg_builder

# 3. MONKEY-PATCH: Swap the original prompt out for our custom one in memory
graphgen.models.kg_builder.light_rag_kg_builder.KG_EXTRACTION_PROMPT = KG_EXTRACTION_PROMPT_UCKG
print("\n>>> SUCCESS: Monkey-patched KG_EXTRACTION_PROMPT with UCKG Cybersecurity Prompt! <<<\n")

# 4. Now run the main engine exactly as if we typed 'python3 -m graphgen.run' in the terminal
from graphgen.run import main

if __name__ == "__main__":
    # We must explicitly set sys.argv so argparse in run.py works
    sys.argv = ["run.py", "--config_file", "examples/generate/generate_uckg/uckg_kg_builder_test.yaml"]
    main()
