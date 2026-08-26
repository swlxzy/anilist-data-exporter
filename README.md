# AniList Data Exporter

A lightweight Python tool for exporting AniList anime list data into a compact, AI-friendly JSON file.

The exporter can retrieve anime from any list available on an AniList profile, including default lists and custom lists. It preserves user scores, advanced scores, AniList community ratings, and list structure while keeping the output compact.

## Features

- Export anime from any AniList list
- Select multiple lists at once
- Preserve the order in which lists are selected
- Export custom AniList lists
- Export user scores
- Export advanced scores when available
- Export AniList community average scores
- Handle duplicate anime entries using AniList media IDs
- Preserve decimal scores such as `8.5`, `7.5`, etc.
- Compact JSON output designed to be easy for AI models to read
- Automatically creates a separate folder for each AniList username
- Existing exports are not overwritten
- Works with large anime libraries

## Requirements

- Python 3
- An AniList account
- Internet connection

The script uses Python's standard library, so no additional Python packages are required.

## Installation

Download or clone this repository.

Then make sure Python 3 is installed:

```bash
python --version
```

If your system uses `python3` instead, use:

```bash
python3 --version
```

No external Python packages are required.

## Recommended Folder Structure

The folder structure is completely optional. You can place the script wherever you want.

However, the following structure is recommended for keeping the project and exported files organized:

```text
your-main-directory/
└── anilist-data-exporter/
    └── anilist.py
```

The program will automatically create a folder for the AniList username when an export is generated.

For example:

```text
your-main-directory/
└── anilist-data-exporter/
    ├── anilist.py
    └── Xerithh/
        ├── Completed_TV.json
        ├── Planning.json
        └── Completed_TV_Dropped.json
```

You do not need to manually create the username folder.

## Running the Exporter

Open a terminal in the directory containing the Python file and run:

```bash
python anilist.py
```

Or, if your system uses `python3`:

```bash
python3 anilist.py
```

The program will ask for an AniList username:

```text
AniList username: Xerithh
```

It will then retrieve the lists available on that profile.

## Selecting Lists

After retrieving the profile, the program displays the available lists with their entry counts.

Example:

```text
Lists available on this account:

[1] Completed TV (30)
[2] Completed Movie (13)
[3] Watching (13)
[4] Dropped (1)
[5] Planning (40)
[6] Paused (2)
[7] Completed OVA (10)
[8] Seinen (1)
[9] Completed ONA (7)
[10] Rom-com (1)
[11] SELECT ALL
```

You can select a single list:

```text
1
```

Multiple lists can be selected using commas:

```text
1,5
```

The order matters.

For example:

```text
2,1
```

exports the second list first and the first list second.

Likewise:

```text
1,2
```

exports the first list first and the second list second.

This allows the resulting JSON to preserve the order chosen by the user.

## Select All

The `SELECT ALL` option exports every list available on the profile.

Example:

```text
[11] SELECT ALL
```

Then enter:

```text
11
```

The program will process all available lists.

## Output

Each export is stored inside a folder named after the AniList username.

For example:

```text
Xerithh/
└── Completed_TV_Dropped.json
```

The filename is based on the selected lists.

This means different exports do not overwrite each other.

For example:

```text
Xerithh/
├── Completed_TV.json
├── Planning.json
├── Dropped.json
└── Completed_TV_Dropped.json
```

The username folder is created automatically if it does not already exist.

## JSON Format

The exported data uses a compact JSON structure.

Example:

```json
{
  "summary": {
    "total": 3,
    "lists": {
      "Paused": 2,
      "Dropped": 1
    }
  },
  "lists": {
    "Paused": [
      {
        "title": "The Apothecary Diaries",
        "average": 88,
        "emptyAdvanced": 8
      },
      {
        "title": "Great Pretender",
        "average": 81,
        "emptyAdvanced": 8
      }
    ],
    "Dropped": [
      {
        "title": "Tawawa on Monday",
        "average": 61,
        "emptyAdvanced": 8
      }
    ]
  }
}
```

The actual output is minified to reduce file size.

## Score Data

The exporter does not convert or reinterpret user scores.

The score returned by AniList's API is stored as provided.

For example, if AniList returns:

```json
"score": 8.5
```

the exporter keeps:

```json
"score": 8.5
```

If AniList returns:

```json
"score": 85
```

the exporter keeps:

```json
"score": 85
```

This allows the exporter to work with different AniList scoring systems without making assumptions about the user's preferred scale.

## Advanced Scores

When advanced scores are available, they are exported directly.

Example:

```json
"advanced": {
  "story": 7.5,
  "characters": 8,
  "visuals": 9.9,
  "audio": 3.37,
  "enjoyment": 0.6
}
```

Unused advanced score categories are not written individually. Instead, their number is stored using `emptyAdvanced`.

Example:

```json
"emptyAdvanced": 5
```

If no advanced scores were provided, there may be no `advanced` object.

## Community Average

The `average` field represents the AniList community average score for that anime.

Example:

```json
{
  "title": "Monster",
  "score": 9.3,
  "average": 88
}
```

`score` and `average` are separate values:

- `score` = the user's score
- `average` = AniList's community average

The exporter does not modify either value.

## Duplicate Handling

The exporter uses AniList media IDs to identify anime.

If the same anime appears in multiple selected lists, the exporter handles duplicates using these IDs according to the selected-list processing rules.

This is especially useful when selecting custom lists together with standard lists.

## Why Compact JSON?

The output is intentionally compact.

Large anime libraries can contain thousands of entries, so unnecessary formatting and repeated information would increase the file size without adding useful data.

The exported JSON is designed to be:

- Small
- Fast to generate
- Easy to transfer
- Easy for AI models to process
- Easy to parse programmatically

## AI Usage

The exported JSON can be provided to an AI model for tasks such as:

- Anime taste analysis
- Finding patterns in your ratings
- Comparing your ratings with AniList averages
- Identifying highly rated genres or styles
- Finding underrated or overrated anime according to your preferences
- Recommending anime based on your existing library
- Analyzing advanced scores such as story, characters, visuals, audio, and enjoyment

Example prompt:

```text
Analyze my anime preferences using this JSON.

Look for:
- genres and themes I consistently rate highly
- anime where my score differs significantly from the AniList average
- patterns in my advanced scores
- directors, studios, or franchises I seem to prefer
- recommendations based on my highest-rated anime
```

## Notes

- The exporter requires an internet connection because it retrieves data from AniList.
- The AniList username must be publicly accessible.
- User scores and advanced scores depend on the data available through AniList's API.
- The exporter does not attempt to guess a user's scoring system.
- The exporter does not convert scores between different scales.
- No additional Python packages are required.

## License

MIT License
