# OpenCNAM Caller ID Validator

This Python application validates phone numbers and retrieves Caller IDs using the OpenCNAM API via the python-opencnam library. It processes a CSV file containing phone numbers, validates them using libphonenumber, and outputs the results to another CSV file. The application uses concurrent processing and implements rate limiting to optimize performance and API usage.

## Requirements

- Python 3.6+
- Virtual environment (venv)
- Required libraries (specified in requirements.txt)

## Installation

1. Clone this repository or download the script.
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     source venv/bin/activate
     ```
4. Install the required libraries:
   ```
   pip install -r requirements.txt
   ```
5. Set up your OpenCNAM credentials as environment variables:
   - On Unix-like systems, you can add these lines to your `.bashrc` or `.bash_profile`:
     ```
     export OPENCNAM_ACCOUNT_SID=your_account_sid_here
     export OPENCNAM_AUTH_TOKEN=your_auth_token_here
     ```
   - On Windows, you can set these through the System Properties > Advanced > Environment Variables dialog, or use the `setx` command:
     ```
     setx OPENCNAM_ACCOUNT_SID your_account_sid_here
     setx OPENCNAM_AUTH_TOKEN your_auth_token_here
     ```

## Usage

Run the script from the command line with the following syntax:

```
python opencnam_validator.py --input input_file.csv --output output_file.csv [--workers N]
```

- `--input`: The input CSV file containing phone numbers (one per line)
- `--output`: The output CSV file where results will be written
- `--workers`: (Optional) The number of concurrent workers (default: 5)

## Help

To view the help menu, run:

```
python opencnam_validator.py --help
```

## Output

The script will generate a CSV file with three columns:
1. Original Phone Number
2. Validated Phone Number (E.164 format or "Invalid")
3. Caller ID (or "Not found" if no match, "Error" if an API error occurred, "Invalid phone number" if validation failed)

The script also logs its progress and any errors to the console.

## Phone Number Validation

The script uses libphonenumber to validate phone numbers. It assumes US numbers but will properly format and validate them. Invalid numbers will not be sent to the OpenCNAM API.

## OpenCNAM Integration

This script uses the python-opencnam library to interact with the OpenCNAM API. Make sure your OpenCNAM account has sufficient credits for the number of lookups you plan to perform.

## Concurrency and Rate Limiting

The script uses concurrent processing to improve performance. You can adjust the number of concurrent workers using the `--workers` argument.

Rate limiting is implemented to ensure the script doesn't exceed 5 requests per second to the OpenCNAM API. This limit can be adjusted in the script if needed.