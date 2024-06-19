import re
import json
import subprocess
import logging
import os
import argparse


def create_logger() -> logging.Logger:
    """
    Create a logger instance for logging messages.

    Returns:
        logging.Logger: The logger instance.
    """
    logger = logging.getLogger("autoreqs")
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler("autoreqs.log", mode="w")
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


def extract_imports_from_py(file_path: str) -> list[str]:
    """
    Extract import statements from a Python file.

    Args:
        file_path (str): The path to the Python file.

    Returns:
        list[str]: A list of imported packages.
    """
    logger = logging.getLogger("autoreqs")
    try:
        with open(file_path, "r") as file:
            content = file.read()
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return []

    import_statements = re.findall(
        r"^\s*(import|from)\s+([a-zA-Z0-9_\.]+)", content, re.MULTILINE
    )

    imported_packages = set()
    for statement in import_statements:
        imported_packages.add(statement[1].split(".")[0])

    return list(imported_packages)


def extract_imports_from_ipynb(file_path: str) -> list[str]:
    """
    Extract import statements from a Jupyter Notebook file.

    Args:
        file_path (str): The path to the Jupyter Notebook file.

    Returns:
        list[str]: A list of imported packages.
    """
    logger = logging.getLogger("autoreqs")
    try:
        with open(file_path, "r") as file:
            if file.read().strip() == "":
                logger.error(f"File is empty: {file_path}")
                return []
            file.seek(0)  # reset file pointer to beginning
            try:
                content = json.load(file)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON: {file_path}")
                return []

    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return []

    imported_packages = set()
    for cell in content.get("cells", []):
        if cell["cell_type"] == "code":
            cell_source = "\n".join(cell["source"])
            import_statements = re.findall(
                r"^\s*(import|from)\s+([a-zA-Z0-9_\.]+)", cell_source, re.MULTILINE
            )
            for statement in import_statements:
                imported_packages.add(statement[1].split(".")[0])
    logger.info(f"Found {len(imported_packages)} packages in {file_path}")

    return list(imported_packages)


def get_pip_freeze() -> dict[str, str]:
    """
    Get the list of installed packages and their versions using `pip freeze`.

    Returns:
        dict[str, str]: A dictionary of package names and versions.
    """
    logger = logging.getLogger("autoreqs")
    try:
        result = subprocess.run(["pip", "freeze"], stdout=subprocess.PIPE)
    except FileNotFoundError:
        logger.error("pip not found")
        return []

    packages = result.stdout.decode("utf-8").strip().split("\n")
    versions = {}
    for pkg in packages:
        temp = pkg.split("==")
        if len(temp) == 2:
            key, val = temp
            versions[key] = val

    logger.info(f"pip freeze found {len(versions)} packages")

    return versions


def compare_packages(
    extracted_packages: list[str], freeze_packages: dict[str, str]
) -> list[str]:
    """
    Compare the extracted packages with the installed packages.

    Args:
        extracted_packages (list[str]): A list of extracted packages.
        freeze_packages (dict[str, str]): A dictionary of installed packages and versions.

    Returns:
        list[str]: A list of missing packages.
    """
    missing_packages = []
    for pkg in extracted_packages:
        if pkg in freeze_packages:
            missing_packages.append(f"{pkg}=={freeze_packages[pkg]}")

    logger = logging.getLogger("autoreqs")
    logger.info(f"Found {len(missing_packages)} missing packages")

    return missing_packages


def find_files_in_folder(folder_path: str, extensions=(".py", ".ipynb")) -> list[str]:
    """
    Find all files with specified extensions in a folder and its subfolders.

    Args:
        folder_path (str): The path to the folder.
        extensions (tuple, optional): The file extensions to search for. Defaults to ('.py', '.ipynb').

    Returns:
        list[str]: A list of file paths.
    """
    logger = logging.getLogger("autoreqs")

    files_list = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(extensions):
                files_list.append(os.path.join(root, file))
    logger.info(f"Found {len(files_list)} files in {folder_path}")

    return files_list


def main(folder_path: str = ".") -> None:
    """
    Main function to analyze Python code and prepare the requirements.txt file.

    Args:
        folder_path (str, optional): Path to the folder to scan for Python files. Defaults to ".".
    """
    create_logger()

    files = find_files_in_folder(folder_path)
    all_imports = set()
    freeze_packages = get_pip_freeze()

    for file in files:
        if file.endswith(".py"):
            all_imports.update(extract_imports_from_py(file))
        elif file.endswith(".ipynb"):
            all_imports.update(extract_imports_from_ipynb(file))

    missing_packages = compare_packages(all_imports, freeze_packages)

    # sort packages by alphabet
    missing_packages.sort()

    req_path = os.path.join(folder_path, "requirements.txt")
    if os.path.exists(req_path):
        logging.warning("requirements.txt already exists. Overwriting it.")
        res = input("Do you want to overwrite the file? (y/n): ")
        if res.lower() != "y":
            return

    logging.info(f"Writing {len(missing_packages)} packages to {req_path}")
    with open(req_path, "wt") as file:
        for pkg in missing_packages:
            file.write(pkg + "\n")
        print(f"Successfully wrote {len(missing_packages)} packages to {req_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Analyze Python code and prepare the requirements.txt file."
    )
    parser.add_argument(
        "folder_path", type=str, help="Path to the folder to scan for Python files."
    )
    args = parser.parse_args()
    main(args.folder_path)
