# AutoReqs

AutoReqs is a Python tool designed to analyze Python code in a specified folder, extract imported packages, and generate a `requirements.txt` file. It scans through `.py` and `.ipynb` files, compares the extracted packages with those installed in your environment, and lists any missing packages.

## Features

- **Extract imports** from Python files (`.py`) and Jupyter Notebooks (`.ipynb`).
- **Compare packages** against installed packages using `pip freeze`.
- **Generate requirements.txt** file with missing packages.
- **Logging** for process tracking and error handling.

## Installation

Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/yourusername/autoreqs.git
cd autoreqs
```

## Usage

Run the script with the folder path containing your Python files as an argument:

```bash
python3 autoreqs.py /path/to/your/folder
```

### Example

```bash
python3 autoreqs.py ./my_project_folder/
```

This command will scan the `my_project_folder` for `.py` and `.ipynb` files, extract the imports, and generate a `requirements.txt` file in the same folder.

## Logging

AutoReqs creates a log file named `autoreqs.log` in the project directory. The log file contains detailed information about the scanning and comparison processes, including any errors encountered.

## Contributing
Feel free to fork the repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License
This project is licensed under the MIT License. If you have any questions, feel free to contact me.