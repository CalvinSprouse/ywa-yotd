# getvid.py

# imports
import argparse
import requests
from datetime import datetime
from pathlib import Path
from os import PathLike
import webbrowser
from bs4 import BeautifulSoup
from rich import print


def get_calendar(dir: PathLike, page_url: str = None, force_dl: bool = False) -> Path:
    """Download the Yoga with Adriene calendar PDF for the current month.
    Args:
        dir (PathLike): Directory to save the calendar PDF.
        page_url (str): URL of the Yoga with Adriene calendar page.
    Returns:
        PathLike: Path to the downloaded calendar PDF.
    Raises:
        ValueError: If no page URL is provided or if no download links are found.
        ConnectionError: If the page cannot be reached or the PDF cannot be downloaded.
        FileNotFoundError: If the specified directory does not exist.
        FileExistsError: If the calendar PDF already exists in the specified directory.
    """

    dir = Path(dir)
    dir.mkdir(exist_ok=True, parents=True)

    format = '%Y%B'
    date = datetime.today().strftime(format)
    file = dir / (str(datetime.today().strftime(format)).lower() + '.pdf')

    if force_dl and file.exists():
        file.unlink()

    if file.exists():
        return file

    if not page_url:
        raise ValueError("No page URL provided.")

    response = requests.get(page_url)
    if response.status_code != 200:
        raise ConnectionError(f"Failed to retrieve calendar from '{page_url}'\nStatus code: {response.status_code}")

    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find_all('a')

    search_str = "Click here to Download the Free PDF"
    dl_links = [a['href'] for a in links if search_str in a.text]
    if not dl_links:
        raise ValueError(f"No download links found for search string '{search_str}'")
    elif len(dl_links) != 1:
        raise ValueError(f"Multiple download links found for search string '{search_str}'")

    pdf_url = dl_links[0]
    pdf_response = requests.get(pdf_url)
    if pdf_response.status_code != 200:
        raise ConnectionError(f"Failed to download PDF from '{pdf_url}'\nStatus code: {pdf_response.status_code}")
    with open(file, 'wb') as f:
        f.write(pdf_response.content)

    return file


def open_calendar(file: PathLike, using: str = None):
    """Open the downloaded calendar PDF in a web browser.
    Args:
        path (PathLike): Path to the calendar PDF.
        using (str): Name of the web browser to use for opening the PDF.
    Raises:
        FileNotFoundError: If the specified path does not exist.
        ValueError: If no web browser is found with the specified name.
        webbrowser.Error: If there is an issue opening the file in the web browser.
    """

    file = Path(file)
    if not file.exists():
        raise FileNotFoundError(f"File '{file}' does not exist.")

    browser = webbrowser.get(using=using)
    if not browser:
        raise ValueError(f"No web browser found with name '{using}'")

    browser.open_new(f"file://{file.resolve()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download and open the Yoga with Adriene calendar."
    )
    parser.add_argument(
        '--dir',
        type=str,
        default=None,
        help='Directory to save the calendar PDF.'
    )
    parser.add_argument(
        '--using',
        type=str,
        default='firefox',
        help='Web browser to use for opening the calendar.'
    )
    parser.add_argument(
        '--force-dl',
        action='store_true',
        help='Force download the calendar even if it already exists.'
    )
    args = parser.parse_args()

    if args.dir is None:
        args.dir = Path(__file__).parent / '.calendars'

    file_path = get_calendar(
        dir=Path(args.dir),
        page_url=r'https://yogawithadriene.com/calendar/',
        force_dl=args.force_dl
    )

    open_calendar(
        file=file_path,
        using=args.using,
    )
