# AniList Data Exporter

A small Python utility for exporting your AniList anime lists to JSON.

It lets you export one or more AniList lists while keeping useful information such as your scores, community scores, advanced scores, dates, and notes. The exported data can also be converted to an Excel spreadsheet.

## Features

* Export anime from one or more AniList lists
* Export custom AniList lists
* Preserve user scores as returned by AniList
* Include AniList community average scores
* Optionally include advanced scores
* Optionally include start/end dates and notes
* Avoid duplicate entries when an anime appears in multiple lists
* Save exports locally as JSON
* Convert exported JSON files to `.xlsx`

## Requirements

* Python 3.x
* An AniList username

The exporter does **not** require your AniList password or access token.

The Excel converter additionally requires:

```bash
pip install openpyxl
```

## Installation

Clone the repository:

```bash
git clone https://github.com/swlxzy/anilist-data-exporter.git
cd anilist-data-exporter
```

No additional packages are required to run `anilist.py`.

## Usage

Run the exporter:

```bash
python anilist.py
```

On Windows, you can also use:

```bash
py anilist.py
```

Enter your AniList username when prompted, then select the lists you want to export.

You can export individual lists or select all available lists.

## Export Options

The exporter provides different levels of detail depending on what you need.

### Basic data

Includes information such as:

* Anime title
* Your score
* AniList community score

### Detailed data

Can additionally include:

* Start date
* Completion date
* Notes
* Advanced scores

This allows you to choose between a smaller export and a more complete backup of your list data.

## Output

Exports are saved locally in a folder named after your AniList username.

For example:

```text
your-project/
├── anilist.py
├── xlsx_converter.py
└── YourUsername/
    ├── Completed.json
    ├── Watching.json
    └── Planning.json
```

The exact filenames depend on the lists you choose to export.

### Example

A basic entry may look like:

```json
{
  "title": "Example Anime",
  "score": 9,
  "average": 8.7
}
```

## Excel Export

If you want to view or edit your exported data in Excel, run:

```bash
python xlsx_converter.py
```

The converter reads the generated JSON files and creates `.xlsx` files using `openpyxl`.

Each AniList list is placed in its own worksheet.

## Privacy

The exporter communicates with the AniList GraphQL API to retrieve your list data.

It does not require your AniList password or access token, and exported files are saved locally on your computer.

Keep in mind that exported data may contain personal information you have added to AniList, such as notes. Do not share your exported files publicly unless you are comfortable sharing their contents.

## Limitations

* This tool is an **exporter**, not a synchronization tool.
* It does not modify your AniList account.
* It does not add, remove, or update anime on AniList.
* API availability and rate limits are determined by AniList.

## Contributing

Bug reports, suggestions, and pull requests are welcome.

If you find an issue or have an idea for an improvement, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License.

See [`LICENSE`](LICENSE) for details.
