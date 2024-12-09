import argparse
import subprocess
import json
import sys
import logging
from pathlib import Path
from pydantic import BaseModel, ValidationError


# Define Pydantic models for structured output
class Finding(BaseModel):
    filename: str
    line_range: str
    description: str


class ErrorModel(BaseModel):
    exit_code: int
    error_message: str


# Configure logging
def setup_logger():
    """
    Configure and return a logger instance with both file and console handlers.
    """
    logger = logging.getLogger('gitleaks_detection')
    logger.setLevel(logging.INFO)

    # Create formatters
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    # File handler
    file_handler = logging.FileHandler('gitleaks_detection.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# Create logger instance
logger = setup_logger()


def write_error_to_file(output_path, error_model):
    """
    Write structured error message to the specified output file.
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
    with output_file.open("w", newline="\n") as f:
        json.dump(error_model.model_dump(), f, indent=4)
        f.write("\n")
    logger.error(f"Error written to file: {output_path}")


def run_gitleaks(args, output_path):
    try:
        # Execute Gitleaks with provided arguments
        result = subprocess.run(args, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("Gitleaks scan completed successfully with no leaks")
            return result
        elif result.returncode == 1:
            # Findings detected (normal behavior for Gitleaks)
            logger.warning("Gitleaks detected findings. Proceeding with output processing...")
            return result
        else:
            # For other non-zero exit codes, raise an exception
            raise subprocess.CalledProcessError(result.returncode, args, result.stderr)

    except subprocess.CalledProcessError as e:
        stderr_message = e.output.strip() if e.output else "No error message captured."

        # Check for specific error patterns
        if "unknown flag" in stderr_message:
            unknown_flag = stderr_message.split("unknown flag: ")[-1].split("\n")[0]
            error = ErrorModel(
                exit_code=2,
                error_message=f"Gitleaks scan failed: unknown argument '{unknown_flag}'."
            )
        else:
            error = ErrorModel(
                exit_code=e.returncode,
                error_message=f"Gitleaks scan failed: {stderr_message}"
            )

        # Print and write the error to the output file
        logger.error(json.dumps(error.model_dump(), indent=4))
        write_error_to_file(output_path, error)
        sys.exit(e.returncode)


def process_output(output_path):
    try:
        # Ensure the output path is a file
        output_file = Path(output_path)
        if not output_file.is_file():
            # If file does not exist, create it with an empty structure
            output_file.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
            logger.info(f"Creating new output file: {output_file}")
            with output_file.open("w") as f:
                json.dump([], f)  # Write an empty JSON array to the file

        # Read and process Gitleaks output
        with output_file.open("r") as f:
            raw_data = json.load(f)

        # Use the Finding model to validate and structure the data
        findings = [
            Finding(
                filename=item["File"],
                line_range=f"{item['StartLine']}-{item['EndLine']}",
                description=item["Description"]
            ).model_dump()  # Convert the Finding object back to a dictionary
            for item in raw_data
        ]

        structured_output = {"findings": findings}

        # Write the structured output back to the output file
        with output_file.open("w") as f:
            json.dump(structured_output, f, indent=4)

        logger.info(json.dumps(structured_output, indent=4))

    except (FileNotFoundError, ValidationError, KeyError) as e:
        error = ErrorModel(exit_code=1, error_message=str(e))
        logger.error(json.dumps(error.model_dump(), indent=4))
        write_error_to_file(output_path, error)  # Write error to output file
        sys.exit(1)


class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        """
        Override the default error method to handle errors gracefully.
        """
        additional_message = (
            "Please provide the arguments like this:\n "
            "--source \"the source path\" --report-path \"the report path\" {gitleaks command} "
            "gitleaks subcommand (e.g., detect, protect, etc.) additional args (e.g --no-git)"
        )
        full_message = f"{message} \n\n {additional_message}"

        error = ErrorModel(exit_code=2, error_message=f"Gitleaks scan failed: {full_message}")
        logger.error(json.dumps(error.model_dump(), indent=4))
        write_error_to_file("output.json", error)  # Write to output file or any default path
        sys.exit(2)


def parse_arguments():
    """
    Parse command-line arguments using argparse.
    """
    # Custom usage string
    usage = (
        "gitleaks_detection.py [-s SOURCE] [-rp REPORT_PATH] "
        "[command] [subcommand] [additional arguments] "
    )

    parser = CustomArgumentParser(
        description="Run Gitleaks and process its output. (args order is important)",
        usage=usage
    )

    # Positional arguments
    parser.add_argument("command", nargs="?", choices=["gitleaks"], default="gitleaks",
                        help="Command to execute (e.g., gitleaks)")
    parser.add_argument("subcommand", nargs="?", default="detect",
                        help="Subcommand for Gitleaks (e.g., detect, protect, etc.)")

    parser.add_argument("-s", "--source", required=False,
                        help="Source directory or file to scan")
    parser.add_argument("-rp", "--report-path", default="output.json",
                        help="Path to save the Gitleaks report")

    # Catch-all for additional arguments
    parser.add_argument("additional", nargs=argparse.REMAINDER,
                        help="Additional arguments for Gitleaks")

    # Parse the arguments
    return parser.parse_args()


if __name__ == "__main__":
    # Parse arguments
    args = parse_arguments()

    # Validate source folder
    source = args.source or None
    if not source:
        error = ErrorModel(exit_code=2, error_message=f"Gitleaks scan failed: please provide a source folder")
        logger.error(json.dumps(error.model_dump(), indent=4))
        write_error_to_file("output.json", error)  # Write to output file or any default path
        sys.exit(2)
    else:
        source_path = Path(source)
        if not source_path.exists():
            error = ErrorModel(exit_code=2, error_message=f"Gitleaks scan failed: please provide a valid source folder")
            logger.error(json.dumps(error.model_dump(), indent=4))
            write_error_to_file("output.json", error)  # Write to output file or any default path
            sys.exit(2)

    # Validate and create the report path
    report_path = Path(args.report_path)
    if not report_path.parent.exists():
        report_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created missing directories for report path: {report_path.parent}")

    # Construct Gitleaks arguments
    gitleaks_args = [
        args.command,
        args.subcommand,
        "--source", str(args.source),
        "--report-path", str(args.report_path),
    ]
    if args.additional:
        gitleaks_args += args.additional

    # Run Gitleaks and process the output
    run_gitleaks(gitleaks_args, args.report_path)
    process_output(args.report_path)
