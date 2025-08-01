import json
import os

def json_to_plain_text():
    """
    Prompts the user for a JSON file path, converts its contents to plain text,
    and saves the output to a new .txt file in the root directory.
    """
    json_file_path = input("Please enter the path to your JSON file: ")

    # Check if the file exists
    if not os.path.exists(json_file_path):
        print(f"Error: The file '{json_file_path}' does not exist.")
        return

    # Create the output file path in the root directory
    output_filename = os.path.basename(json_file_path).replace('.json', '.txt')
    output_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_filename)

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        with open(output_file_path, 'w', encoding='utf-8') as f_out:
            # Recursive function to extract values and write to file
            def extract_values(obj):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        f_out.write(f"{key}: ")
                        extract_values(value)
                elif isinstance(obj, list):
                    for item in obj:
                        extract_values(item)
                else:
                    f_out.write(str(obj) + "\n")

            extract_values(data)
        
        print(f"Successfully converted '{json_file_path}' to plain text.")
        print(f"Output saved to '{output_file_path}'")

    except json.JSONDecodeError:
        print(f"Error: The file '{json_file_path}' is not a valid JSON file.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Run the function
if __name__ == "__main__":
    json_to_plain_text()