import requests
import json
import os
import argparse


def generate_perplexity_definition(cell_type: str, api_key: str) -> dict | None:
    """
    Calls the Perplexity API to generate a definition for a given cell type
    using the detailed prompt.

    Returns the JSON response from the API or None if an error occurs.
    """
    url = "https://api.perplexity.ai/chat/completions"

    # The updated prompt requesting DOIs is used here.
    payload = {
        # Changed model sonar-pro
        "model": "sonar-pro",
        "messages": [
            {
                # System Role content.
                "role": "system",
                "content": "You are an expert cell biologist with extensive experience in creating precise and informative descriptions of cell types for ontologies.",
            },
            {
                # User Role content with all detailed instructions.
                "role": "user",
                "content": f"""Generate a definition for the cell type '{cell_type}', basing the definition on evidence from primary scientific literature and major review articles. Each definition should:
Avoid naming the cell type being defined directly. It should start with a statement of a general classification for the cell type being defined, followed by the characteristics that distinguish it from other cell types within the same general classification.
Describe distinguishing characteristics, including structural features, functional roles, and anatomical context.
Include species-specific information when relevant, noting presence or absence in different organisms.
Mention key molecular markers, transcription factors, or genes only if they are crucial for identification or development of the cell type. When including molecular markers, specify the species in which they have been identified (e.g., "marker X in mice", "marker Y in humans").
For general cell types, focus on common features across different tissues or organs.
Include supporting references to key statements of the definition rather than listing them at the end.
Be concise yet comprehensive, aiming for 80-120 words in a single paragraph.
Use clear, scientific language accessible to biologists across various specialties.
Example output for a specific cell type: "A tuft cell that is part of the medullary epithelium of the thymus, characterized by lateral microvilli and specific markers, including L1CAM (1) in both mice and humans, as well as MHC II in mice (1,2). This cell is pivotal in immune functions such as antigen presentation, central tolerance, and type 2 immunity. It exhibits characteristics of both a medullary thymic epithelial cell (mTEC) and a peripheral tuft cell. Its development is governed by transcription factors such as POU2F3 (3,4)."

Please generate a definition for the following cell type: '{cell_type}'""",
            },
        ],
        "max_tokens": 512,
        "temperature": 0.2,
        "top_p": 0.9,
        "return_citations": True,
        "return_images": False,
        "return_related_questions": False,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raises an exception for bad status codes (4xx or 5xx)
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"  > HTTP Error for {cell_type}: {err}")
        print(f"  > Response content: {err.response.text}")
        return None
    except Exception as e:
        print(f"  > An error occurred for {cell_type}: {e}")
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

    cell_types_to_process = ["paneth cell", "tendon cell", "astrocyte"]

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
