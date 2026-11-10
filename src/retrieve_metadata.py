"""
This script retrieves the JSON metadata for a Figshare item.
"""

import argparse
import json
import sys
from pathlib import Path

import requests


def validate_plain_whole_number(value: str) -> int:
    """
    This function is intended to validate that Figshare item IDs passed to the
    program are formatted as positive, plain whole numbers.
    """
    # Filter decimals and non-base 10 values such as octals, hex values, etc.
    try:
        input_number = int(value, 10)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Use a whole number (base 10).") from exc

    # Filter values that are negative or zero.
    if input_number <= 0:
        raise argparse.ArgumentTypeError("Use a positive number.")

    return input_number


def main():
    """
    This function holds the main Figshare metadata retrieval functionality.
    """
    # It's assumed the Figshare item ID is passed as an input parameter.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "figshare_item_id",
        type=validate_plain_whole_number,
        help="a required whole number (no decimals)",
    )
    args = parser.parse_args()
    figshare_item_id = args.figshare_item_id

    # Get the directory of the current script.
    dir_current = Path(__file__).resolve().parent

    # Prepare to save the metadata to the data directory.
    dir_data = dir_current.parent / "data"
    dir_data.mkdir(exist_ok=True)
    file_path = dir_data / f"figshare-metadata-{figshare_item_id}.json"

    # Set the Figshare item URL.
    url: str = f"https://api.figshare.com/v2/articles/{figshare_item_id}"

    # Gracefully handle URL, Figshare server or network connection issues.
    try:
        # Send a HTTP GET request to the target URL.
        # N.B. A timeout has been specified to ameliorate hung sessions.
        response = requests.get(url, timeout=30)

        # Raise an error if the HTTP status code indicates a failed request.
        response.raise_for_status()
    except requests.exceptions.Timeout as error:
        print(f"Figshare timeout error: {error}. Exiting.", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.ConnectionError as error:
        print(f"Figshare connection error: {error}. Exiting.", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.HTTPError as error:
        print(f"Figshare request error: {error}. Exiting.", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.RequestException as error:
        print(f"Figshare request failed: {error}. Exiting.", file=sys.stderr)
        sys.exit(1)

    # Get the JSON metadata for the Figshare item.
    try:
        metadata: dict = response.json()
    except requests.exceptions.JSONDecodeError as error:
        print(f"Figshare returned invalid JSON: {error}. Exiting.", file=sys.stderr)
        sys.exit(1)

    # Save the JSON metadata to a local file.
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)


# Execute "main()" if the script is run directly, skip it otherwise.
if __name__ == "__main__":
    main()
