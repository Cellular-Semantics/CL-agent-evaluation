import os
import openai
import subprocess
import json
import yaml
import argparse


def set_runoak_api_key():
    """
    Sets the BioPortal API key for runoak by reading it from an
    environment variable. This is more secure and portable than
    hardcoding the key and path.
    """
    try:
        # Retrieve key from environment variable for security.
        bioportal_api_key = os.environ.get("BIOPORTAL_API_KEY")
        if not bioportal_api_key:
            raise ValueError(
                "BIOPORTAL_API_KEY environment variable not set. "
                "Please set it before running the script."
            )

        subprocess.run(
            [
                "runoak",
                "set-apikey",
                "-e",
                "bioportal",
                bioportal_api_key,
            ],
            check=True,
            # Suppress stdout/stderr unless there's an error
            capture_output=True,
        )
        print("runoak API key for bioportal has been set successfully.")
    except subprocess.CalledProcessError as e:
        # Provide more helpful error feedback
        print(f"Failed to set runoak API key. Error: {e.stderr.decode().strip()}")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except FileNotFoundError:
        print(
            "Error: 'runoak' command not found. "
            "Is OAK installed and in your system's PATH? "
            "Try running this script with 'poetry run python extended_defs.py'"
        )


def generate_description(cell_type):
    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    # UP TO DATE detailed prompt is used.
    prompt = f"""System Role: You are an expert cell biologist with extensive experience in creating precise and informative descriptions of cell types for ontologies.
User Role: I need you to create definitions for specific cell types to be included in the Cell Ontology. Each definition should:
Avoid naming the cell type being defined directly. It should start with a statement of a general classification for the cell type being defined, followed by the characteristics that distinguish it from other cell types within the same general classification.
Describe distinguishing characteristics, including structural features, functional roles, and anatomical context.
Include species-specific information when relevant, noting presence or absence in different organisms.
Mention key molecular markers, transcription factors, or genes only if they are crucial for identification or development of the cell type. When including molecular markers, specify the species in which they have been identified (e.g., "marker X in mice", "marker Y in humans").
For general cell types, focus on common features across different tissues or organs.
Include supporting references to key statements of the definition rather than listing them at the end.
Be concise yet comprehensive, aiming for 80-120 words in a single paragraph.
Use clear, scientific language accessible to biologists across various specialties.
Example output for a specific cell type: "A tuft cell that is part of the medullary epithelium of the thymus, characterized by lateral microvilli and specific markers, including L1CAM (1) in both mice and humans, as well as MHC II in mice (1,2). This cell is pivotal in immune functions such as antigen presentation, central tolerance, and type 2 immunity. It exhibits characteristics of both a medullary thymic epithelial cell (mTEC) and a peripheral tuft cell. Its development is governed by transcription factors such as POU2F3 (3,4)." 

Please generate a definition for the following cell type: '{cell_type}'"""

    try:
        chat_completion = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=500,
        )

        if chat_completion.choices and len(chat_completion.choices) > 0:
            return chat_completion.choices[0].message.content.strip()
        else:
            return "No valid completion found."
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def split_and_categorize_definition(cell_type, definition):
    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    prompt = "You are an assistant specialized in processing scientific definitions for a knowledge base."

    user = (
        f'Please analyze the following definition of "{cell_type}" and split it into individual, concise statements. '
        f"Each statement should be categorized under one of the following headings:\n"
        f"1. **Location**\n"
        f"2. **Structure**\n"
        f"3. **Cellular Component**\n"
        f"4. **Biological Process**\n"
        f"5. **Relationships to Diseases**\n\n"
        f"IMPORTANT: Ensure that each statement starts with the phrase '{cell_type}' and is a complete thought. "
        f"Do not vary the phrasing or start with other words.\n\n"
        f"Definition:\n{definition}\n\n"
        f"Please return only the categorized statements in the following JSON format:\n\n"
        f"```json\n"
        f"{{\n"
        f'    "Location": [\n'
        f'        "Statement 1",\n'
        f'        "Statement 2"\n'
        f"    ],\n"
        f'    "Structure": [\n'
        f'        " Statement 1",\n'
        f'        " Statement 2"\n'
        f"    ],\n"
        f'    "Cellular Component": [\n'
        f'        "Statement 1",\n'
        f'        "Statement 2"\n'
        f"    ],\n"
        f'    "Biological Process": [\n'
        f'        "Statement 1",\n'
        f'        "Statement 2"\n'
        f"    ],\n"
        f'    "Relationships to Diseases": [\n'
        f'        "Statement 1",\n'
        f'        "Statement 2"\n'
        f"    ]\n"
        f"}}\n"
        f"```"
    )

    try:
        chat_completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user},
            ],
            max_tokens=800,
        )

        if chat_completion.choices and len(chat_completion.choices) > 0:
            response_content = chat_completion.choices[0].message.content.strip()
            # Extract JSON from the response
            json_start = response_content.find("{")
            json_end = response_content.rfind("}") + 1
            json_str = response_content[json_start:json_end]
            return json.loads(json_str)
        else:
            print("No valid completion found.")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# Run ontogpt to ground definitions for GO cellular components and biological process terms.
def extract_information():
    try:
        # Run the extraction command
        result = subprocess.run(
            [
                "ontogpt",
                "extract",
                "-t",
                "cell_process",
                "-i",
                "descriptions.txt",
                "--model",
                "gpt-4o",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        print("Extraction successful. Output:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Failed to extract information:", e)


def main(output_dir):
    set_runoak_api_key()
    # Ensure the output directory exists. If not, create it.
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output will be saved to: {os.path.abspath(output_dir)}")

    # Add as many cell types as you want to this list.
    cell_types_to_process = [
        "tendon cell",
        "thymic tuft cell",
        "astrocyte",
        "intestinal subserosal fibroblast",
    ]

    # This loop processes each cell type completely before moving to the next.
    for cell_type in cell_types_to_process:
        print(f"--- Processing: {cell_type.upper()} ---")

        description = generate_description(cell_type)

        if not description:
            print(f"Failed to generate description for {cell_type}. Skipping.\n")
            continue  # Move to the next cell type

        # Create a safe filename based on the cell type
        base_filename = cell_type.replace(" ", "_")
        description_filename = f"{base_filename}_description.txt"

        # Construct the full path for the description file
        description_filepath = os.path.join(output_dir, description_filename)

        # Save the description to its own unique text file using the full path variable .
        with open(description_filepath, "w") as file:
            file.write(description)
        print(f"Description for {cell_type} saved to {description_filepath}")

        # Categorize the description we just generated
        categorized_statements = split_and_categorize_definition(cell_type, description)

        if not categorized_statements:
            print(
                f"Failed to categorize definition for {cell_type}. Skipping YAML generation.\n"
            )
            continue  # Move to the next cell type

        # Process and save the YAML file
        all_statements = []
        for statements in categorized_statements.values():
            all_statements.extend(statements)

        formatted_statements = {
            "label": {
                f"assertion{i+1}": statement
                for i, statement in enumerate(all_statements)
            }
        }

        statements_filename = f"{base_filename}_statements.yaml"

        # Construct the full path for the statements file
        statements_filepath = os.path.join(output_dir, statements_filename)

        # Save the categorized statements to a YAML file using the full path variable.
        with open(statements_filepath, "w") as yaml_file:
            yaml.dump(formatted_statements, yaml_file, sort_keys=False, indent=2)

        print(
            f"Categorized statements for {cell_type} written to {statements_filepath}.\n"
        )

    print("--- All processing complete. ---")

    # extract_information()


if __name__ == "__main__":
    # Get the absolute path of the directory containing this script (e.g., .../src)
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Get the parent directory of script_dir (this will be the project root)
    project_root = os.path.dirname(script_dir)

    # Set the default output directory to be the new dedicated subdirectory.
    default_output_path = os.path.join(
        project_root, "output", "chatgpt_and_citeseek_output"
    )

    # Set up the command-line argument parser
    parser = argparse.ArgumentParser(
        description="Generate cell type descriptions and categorized statements."
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output_dir",
        default=default_output_path,  # Use the new, nested default path
        help=f"The directory where output files will be saved. Defaults to: {default_output_path}",
    )
    args = parser.parse_args()

    # Check for the API key before running.
    if not os.environ.get("OPENAI_API_KEY"):
        print("FATAL: OPENAI_API_KEY environment variable is not set. Exiting.")
    else:
        # Pass the parsed output directory to the main function.
        main(args.output_dir)
