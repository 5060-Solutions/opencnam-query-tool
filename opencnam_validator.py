# opencnam_validator.py

import csv
import argparse
import logging
import os
import time
from dotenv import load_dotenv
import phonenumbers
from opencnam import Phone
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Rate limiting configuration
RATE_LIMIT = 5  # requests per second
RATE_LIMIT_PERIOD = 1  # second

class RateLimiter:
    def __init__(self, rate_limit, period):
        self.rate_limit = rate_limit
        self.period = period
        self.calls = []
        self.lock = Lock()

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            with self.lock:
                now = time.time()
                # Remove calls older than the rate limit period
                self.calls = [call for call in self.calls if now - call < self.period]
                
                if len(self.calls) >= self.rate_limit:
                    sleep_time = self.period - (now - self.calls[0])
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                
                self.calls.append(time.time())
            
            return func(*args, **kwargs)
        return wrapper

rate_limiter = RateLimiter(RATE_LIMIT, RATE_LIMIT_PERIOD)

def validate_phone_number(phone_number):
    try:
        parsed_number = phonenumbers.parse(phone_number, "US")
        if not phonenumbers.is_valid_number(parsed_number):
            return None
        return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        return None

@rate_limiter
def get_caller_id(phone_number, account_sid, auth_token):
    try:
        phone = Phone(phone_number, account_sid, auth_token)
        return phone.cnam
    except Exception as e:
        logging.error(f"Error retrieving CNAM for {phone_number}: {str(e)}")
        return "Error"

def process_phone_number(phone_number, account_sid, auth_token):
    validated_number = validate_phone_number(phone_number)
    if validated_number:
        caller_id = get_caller_id(validated_number, account_sid, auth_token)
    else:
        caller_id = "Invalid phone number"
    return phone_number, validated_number or "Invalid", caller_id

def process_csv(input_file, output_file, max_workers, account_sid, auth_token):
    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        # Write header
        writer.writerow(['Original Phone Number', 'Validated Phone Number', 'Caller ID'])
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_number = {executor.submit(process_phone_number, row[0].strip(), account_sid, auth_token): row[0].strip() for row in reader if row}
            
            for future in as_completed(future_to_number):
                original_number = future_to_number[future]
                try:
                    result = future.result()
                    writer.writerow(result)
                    logging.info(f"Processed: {result[0]} - {result[1]} - {result[2]}")
                except Exception as e:
                    logging.error(f"Error processing {original_number}: {str(e)}")
                    writer.writerow([original_number, "Error", "Error"])

def main():
    parser = argparse.ArgumentParser(description="Validate Caller IDs using OpenCNAM API")
    parser.add_argument("--input", required=True, help="Input CSV file containing phone numbers")
    parser.add_argument("--output", required=True, help="Output CSV file for results")
    parser.add_argument("--workers", type=int, default=5, help="Number of concurrent workers (default: 5)")
    args = parser.parse_args()

    account_sid = os.getenv("OPENCNAM_ACCOUNT_SID")
    auth_token = os.getenv("OPENCNAM_AUTH_TOKEN")
    if not account_sid or not auth_token:
        logging.error("OPENCNAM_ACCOUNT_SID or OPENCNAM_AUTH_TOKEN not found in environment variables")
        return

    process_csv(args.input, args.output, args.workers, account_sid, auth_token)
    logging.info("Processing complete")

if __name__ == "__main__":
    main()