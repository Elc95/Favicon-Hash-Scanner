# Favsrcon #

This script scans the favicon of a website and generates a hash of the favicon content. The script supports scanning both single URLs and lists of URLs.

## Features

✅ Randomized User-Agent header for each request.

✅ SSL verification skip for IP-based URLs over HTTPS (user confirmation).

✅ Customizable verbosity output with `--quiet` and `--verbose` flags.

✅ Output saved as `domain_name.txt` or `output.txt` in the `/results` folder.

## Usage

1. Clone the repository:
   ```bash
   git clone https://github.com/Elc95/Favsrcon.git
   cd Favsrcon
2. Install dependencies:
   pip install -r requirements.txt
   or
   pip3 install -r requirements.txt
3. Run the script:
   - For a single URL:
     python3 favsrcon.py https://example.com
   - For a list of URLs (in urls.txt):
     python3 favsrcon.py urls.txt
4. To run with verbosity or quiet mode:
     --verbose (default): Detailed output
     --quiet: Only critical errors and results
   Example:
   python favsrcon.py https://example.com --quiet
5. Output
   Results will be saved in the /results folder as:
   domain_name.txt (for single URLs)
   output.txt (for multiple URLs)
