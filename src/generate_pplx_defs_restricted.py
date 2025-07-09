import requests
import json
import os
import argparse


def generate_perplexity_definition(cell_type: str, api_key: str) -> dict | None:
    """
    Calls Perplexity API with a restricted query and specific citation formatting.
    """
    url = "https://api.perplexity.ai/chat/completions"

    payload = {
        "model": "sonar-deep-research",
        "messages": [
            {
                "role": "system",
                "content": "You are an expert cell biologist. Your answers must be based on primary scientific literature and major reviews from peer-reviewed sources.",
            },
            {
                "role": "user",
                "content": f"""Provide a detailed overview of the cell type '{cell_type}'.
                
Your response must adhere to the following rules:
1.  Base all statements on evidence from primary scientific literature.
2.  After the overview, provide a "References" section.
3.  For each reference, format it as: 'Author, (Year). Title. Journal, Volume(Issue), pages. DOI: [DOI]'. You must include the DOI.
""",
            },
        ],
        "return_citations": True,
        "search_domain_filter": [
            "pubmed.ncbi.nlm.nih.gov",
            "ncbi.nlm.nih.gov/pmc/",
            "sciencedirect.com",
            "nature.com",
            "cell.com",
            "frontiersin.org",
            "journals.plos.org",
        ],
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"  > HTTP Error: {err}")
        print(f"  > Response content: {err.response.text}")
        return None
    except Exception as e:
        print(f"  > An error occurred: {e}")
        return None


def main(output_dir: str):
    """
    Main function to process a list of cell types and save their definitions.
    """
    api_key = os.environ.get("PPLX_API_KEY")
    if not api_key:
        print("FATAL: PPLX_API_KEY environment variable is not set. Exiting.")
        return

    os.makedirs(output_dir, exist_ok=True)
    print(f"Output will be saved to: {os.path.abspath(output_dir)}")

    cell_types_to_process = ["monocyte-derived Kupffer cell"]

    for cell_type in cell_types_to_process:
        print(f"--- Processing: {cell_type.upper()} ---")
        response_json = generate_perplexity_definition(cell_type, api_key)

        if response_json:
            base_filename = cell_type.replace(" ", "_")
            output_filepath = os.path.join(
                output_dir, f"{base_filename}_perplexity_def.json"
            )

            with open(output_filepath, "w") as f:
                json.dump(response_json, f, indent=4)

            print(
                f"  > Successfully generated definition and saved to {output_filepath}\n"
            )
        else:
            print(f"  > Failed to generate definition for {cell_type}.\n")

    print("--- All processing complete. ---")


if __name__ == "__main__":
    # Get the absolute path of the directory containing this script (e.g., .../src)
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Get the parent directory of script_dir (this will be the project root)
    project_root = os.path.dirname(script_dir)

    # Set the default output directory to be 'output/perplexity_output' inside the project root
    default_output_path = os.path.join(project_root, "output", "perplexity_output")

    # Set up the command-line argument parser
    parser = argparse.ArgumentParser(
        description="Generate cell type definitions using the Perplexity API."
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output_dir",
        default=default_output_path,
        help=f"The directory where output files will be saved. Defaults to: {default_output_path}",
    )
    args = parser.parse_args()

    main(args.output_dir)
