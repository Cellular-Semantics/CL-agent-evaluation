# LLM and Agent-Based Ontology Evaluation

This repository contains a collection of scripts and experiments designed to test and evaluate the use of different Large Language Models (LLMs) and agentic AI systems for generating and curating ontology definitions with references, specifically for the Cell Ontology.

## Prerequisites

Before you begin, ensure you have the following installed and configured:
* Python 3.9+
* [Poetry](https://python-poetry.org/docs/#installation) for dependency management.
* **API Keys** set as environment variables. You will need:
    * `OPENAI_API_KEY`
    * `PPLX_API_KEY` (for running ```src/generate_perplexity_defs_refs.py```)
    * `BIOPORTAL_API_KEY` (for `runoak` used by the OpenAI script)

## Overview

This project explores multiple workflows for generating structured biological information:

1.  **Multi-Step OpenAI & CurateGPT Pipeline** 
    * Uses OpenAI's GPT models to generate detailed definitions.
    * Categorizes those definitions into structured assertions.
    * Finds literature references for each assertion using `curategpt citeseek`.
    * Optionally grounds definitions to Gene Ontology (GO) terms with `ontogpt extract`.

2.  **Single-Step Perplexity API Pipeline** 
    * Generates concise definitions with direct citations in a single API call using Perplexity's online models  (e.g., ```sonar-large-32k-online```).

3.  **Schema Development and Tooling** 
    * Includes command-line tests for `ontogpt` schema extraction and for generating Pydantic data models from LinkML schemas using `gen-pydantic`.

## Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Cellular-Semantics/CL-agent-evaluation.git
    cd CL-agent-evaluation
    ```

2.  **Set up Environment Variables:**
    Create a `.env` file in the project root or export the variables directly in your terminal. For example:
    ```bash
    export OPENAI_API_KEY="sk-..."
    export PPLX_API_KEY="pplx-..."
    export BIOPORTAL_API_KEY="4911280b-..."
    ```


3.  **Install Dependencies:**
    Poetry will create a virtual environment and install all necessary packages from the `pyproject.toml` file.
    ```bash
    poetry install
    ```


## Usage: Experimental Workflows

All commands should be run from the root directory of the project.

---

### Workflow 1: OpenAI + `citeseek`

This workflow uses OpenAI to generate definitions and `curategpt` to find references for structured assertions. The outputs are stored in `output/chatgpt_and_citeseek_output/`.

**Step 1: Generate Definitions and Assertions**

This script uses `gpt-4` to generate definitions, categorizes them into statements, and saves the output as both `.txt` and `.yaml` files.

```bash
poetry run python src/generate_defs_no_refs.py
```

**Step 2: Find References for Assertions**

This script reads the `.yaml` files created in Step 1 and uses `curategpt citeseek` to find literature references for each assertion, saving the results to new `.txt` files.
```bash
poetry run python src/generate_citeseek_references.py
```

---

### Workflow 2: Perplexity API

This workflow uses the Perplexity API (`sonar-large-32k-online`) to generate definitions with citations in a single step. The raw JSON responses are saved to `output/perplexity_output/`.

**Run the Perplexity Definition Generator:**
```bash
poetry run python src/generate_perplexity_defs_refs.py
```

You can specify a different output directory with the `-o` flag:
```bash
poetry run python src/generate_perplexity_defs_refs.py -o path/to/your/output
```

---

### Workflow 3: Schema and `ontogpt` Tooling Tests

These commands are for interacting directly with `ontogpt` and LinkML tools.

**1. Test `ontogpt` extract**

This uses a template to extract structured information from a simple text file.
```bash
poetry run ontogpt extract -t templates/cell_process.yaml -i astrocyte_input.txt
```

**2. Generate Pydantic Models**

This converts a LinkML schema (`.yaml`) into Python Pydantic classes (`.py`), which is useful for data validation and development.
```bash
poetry run gen-pydantic templates/cell_process.yaml > templates/cell_process.py
```
