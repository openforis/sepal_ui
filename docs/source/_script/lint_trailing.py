import os
import sys

from docutils import ApplicationError


def process_file(file_path):
    """Process a single .rst file, checking for validity and fixing whitespace."""
    try:
        with open(file_path, "r") as f:
            content = f.read()
            # publish_string(source=content, writer_name="null")  # Validate RST
        with open(file_path, "w") as f:
            f.writelines([line.rstrip() + "\n" for line in content.splitlines()])
            print("done")
    except (IOError, ApplicationError) as e:
        print(f"Skipping file {file_path}: {e}")


def process_directory(path):
    """Process all .rst files in a directory."""
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".rst"):
                process_file(os.path.join(root, file))


def main():
    """Main function for the script."""
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} path_or_file")
        sys.exit(1)

    path_or_file = sys.argv[1]
    if os.path.exists(path_or_file):
        if os.path.isdir(path_or_file):
            process_directory(path_or_file)
        else:
            process_file(path_or_file)
    else:
        print(f"The path {path_or_file} does not exist.")


if __name__ == "__main__":
    main()
