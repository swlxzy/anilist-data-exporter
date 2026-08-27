import json
import re
import urllib.error
import urllib.request
from pathlib import Path


API_URL = "https://graphql.anilist.co"


BASE_QUERY = """
query ($username: String) {
    MediaListCollection(userName: $username, type: ANIME) {
        lists {
            name
            isCustomList
            status
            entries {
                score
                advancedScores
                media {
                    id
                    averageScore
                    title {
                        english
                        romaji
                    }
                }
            }
        }
    }
}
"""


DETAIL_QUERY = """
query ($username: String) {
    MediaListCollection(userName: $username, type: ANIME) {
        lists {
            name
            isCustomList
            status
            entries {
                score
                advancedScores
                startedAt {
                    year
                    month
                    day
                }
                completedAt {
                    year
                    month
                    day
                }
                notes
                media {
                    id
                    averageScore
                    title {
                        english
                        romaji
                    }
                }
            }
        }
    }
}
"""


def graphql_request(username, query):
    payload = json.dumps({
        "query": query,
        "variables": {
            "username": username
        }
    }).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "AniListDataExporter/1.0"
    }

    request = urllib.request.Request(
        API_URL,
        data=payload,
        headers=headers
    )

    try:
        with urllib.request.urlopen(request) as response:
            data = json.loads(
                response.read().decode("utf-8")
            )

    except urllib.error.HTTPError as error:
        print(f"\nHTTP error: {error.code}")
        return None

    except urllib.error.URLError as error:
        print(f"\nConnection error: {error.reason}")
        return None

    except Exception as error:
        print(f"\nUnexpected error: {error}")
        return None

    if data.get("errors"):
        print("\nAniList API error:")

        for error in data["errors"]:
            print(
                f"- {error.get('message', 'Unknown error')}"
            )

        return None

    return data


def format_date(date_data):
    if not date_data or not date_data.get("year"):
        return None

    year = date_data["year"]
    month = date_data.get("month") or 1
    day = date_data.get("day") or 1

    return f"{year:04d}-{month:02d}-{day:02d}"


def process_entry(entry, detail_mode):
    media = entry.get("media") or {}
    media_id = media.get("id")

    if not media_id:
        return None

    titles = media.get("title") or {}

    anime_title = (
        titles.get("english")
        or titles.get("romaji")
    )

    if not anime_title:
        return None

    item = {
        "title": anime_title
    }

    user_score = entry.get("score")

    if user_score is not None and user_score > 0:
        item["score"] = user_score

    average_score = media.get("averageScore")

    if average_score is not None and average_score > 0:
        item["average"] = average_score

    if detail_mode in (2, 4):
        started = format_date(
            entry.get("startedAt")
        )

        completed = format_date(
            entry.get("completedAt")
        )

        if started:
            item["started"] = started

        if completed:
            item["completed"] = completed

    if detail_mode in (3, 4):
        notes = entry.get("notes")

        if notes:
            item["notes"] = notes

    raw_advanced = entry.get("advancedScores")

    if isinstance(raw_advanced, dict):
        valid_advanced = {}
        empty_count = 0

        for category, score in raw_advanced.items():
            if score is None or score == 0:
                empty_count += 1
            else:
                valid_advanced[category.lower()] = score

        if valid_advanced:
            item["advanced"] = valid_advanced

        if empty_count > 0:
            item["emptyAdvanced"] = empty_count

    return media_id, item


def safe_filename(name):
    name = name.strip()

    name = re.sub(
        r'[<>:"/\\|?*]',
        "_",
        name
    )

    name = re.sub(
        r"\s+",
        "_",
        name
    )

    name = name.strip("._")

    return name or "export"


def unique_filename(directory, filename):
    path = directory / filename

    if not path.exists():
        return path

    stem = path.stem
    suffix = path.suffix
    counter = 2

    while True:
        candidate = (
            directory
            / f"{stem}_{counter}{suffix}"
        )

        if not candidate.exists():
            return candidate

        counter += 1


def parse_selection(raw_input, list_count):
    selected_numbers = []

    for part in raw_input.split(","):
        part = part.strip()

        if not part.isdigit():
            continue

        number = int(part)

        if number not in selected_numbers:
            selected_numbers.append(number)

    if not selected_numbers:
        return None, False

    select_all_number = list_count + 1

    if select_all_number in selected_numbers:
        return list(range(1, list_count + 1)), True

    valid_numbers = [
        number
        for number in selected_numbers
        if 1 <= number <= list_count
    ]

    if not valid_numbers:
        return None, False

    return valid_numbers, False


def get_detail_mode():
    print("\nAdditional data:")
    print(
        "[1] Basic Data Only "
        "(Title + Scores + Average)"
    )
    print("[2] Add Dates (Started / Completed)")
    print("[3] Add Notes")
    print("[4] Add Dates + Notes")

    while True:
        choice = input(
            "\nSelection (1-4) [Default: 1]: "
        ).strip()

        if not choice:
            return 1

        if choice in ("1", "2", "3", "4"):
            return int(choice)

        print("Invalid selection. Please enter 1, 2, 3, or 4.")


def main():
    print("AniList Data Exporter")
    print("---------------------")

    username = input(
        "\nAniList username: "
    ).strip()

    if not username:
        print("Username cannot be empty.")
        return

    detail_mode = get_detail_mode()

    if detail_mode == 1:
        query = BASE_QUERY
    else:
        query = DETAIL_QUERY

    print("\nFetching AniList data...")

    data = graphql_request(
        username,
        query
    )

    if not data:
        return

    collection = (
        data.get("data", {})
        .get("MediaListCollection")
    )

    if not collection:
        print(
            "\nNo lists found. "
            "The profile may be private or unavailable."
        )
        return

    available_lists = collection.get("lists", [])

    if not available_lists:
        print("\nNo anime lists found.")
        return

    print("\nLists available on this account:\n")

    for index, anime_list in enumerate(
        available_lists,
        start=1
    ):
        name = anime_list.get(
            "name",
            "Unnamed"
        )

        entries = anime_list.get(
            "entries",
            []
        )

        print(
            f"[{index}] {name} "
            f"({len(entries)})"
        )

    select_all_number = len(available_lists) + 1

    print(
        f"[{select_all_number}] SELECT ALL"
    )

    raw_selection = input(
        "\nLists to export "
        "(Example: 1 or 2,1,3): "
    ).strip()

    selected_numbers, select_all = parse_selection(
        raw_selection,
        len(available_lists)
    )

    if not selected_numbers:
        print("\nInvalid selection.")
        return

    if select_all:
        selected_lists = available_lists
    else:
        selected_lists = [
            available_lists[number - 1]
            for number in selected_numbers
        ]

    username_folder = safe_filename(username)

    output_directory = (
        Path.cwd() / username_folder
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    result_lists = {}
    summary_counts = {}

    total_anime_count = 0
    total_lists = len(selected_lists)

    print(
        f"\nProcessing {total_lists} "
        f"selected list(s)...\n"
    )

    for list_index, anime_list in enumerate(
        selected_lists,
        start=1
    ):
        list_name = anime_list.get(
            "name",
            "Unnamed"
        )

        entries = anime_list.get(
            "entries",
            []
        )

        processed_entries = []

        # Duplicate control is now local to each list.
        list_seen_ids = set()

        for entry in entries:
            processed = process_entry(
                entry,
                detail_mode
            )

            if not processed:
                continue

            media_id, item = processed

            if media_id in list_seen_ids:
                continue

            list_seen_ids.add(media_id)
            processed_entries.append(item)

        result_lists[list_name] = processed_entries

        summary_counts[list_name] = len(
            processed_entries
        )

        total_anime_count += len(
            processed_entries
        )

        print(
            f"[{list_index}/{total_lists}] "
            f"{list_name}: "
            f"{len(processed_entries)}/"
            f"{len(entries)}"
        )

    final_output = {
        "summary": {
            "total": total_anime_count,
            "lists": summary_counts
        },
        "lists": result_lists
    }

    compressed_json = json.dumps(
        final_output,
        separators=(",", ":"),
        ensure_ascii=False
    )

    if select_all:
        filename = "select_all.json"
    else:
        filename_parts = [
            safe_filename(
                anime_list.get(
                    "name",
                    "Unnamed"
                )
            )
            for anime_list in selected_lists
        ]

        filename = (
            "_".join(filename_parts)
            + ".json"
        )

    output_path = unique_filename(
        output_directory,
        filename
    )

    try:
        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as output_file:
            output_file.write(
                compressed_json
            )

    except OSError as error:
        print(
            f"\nCould not write output file: "
            f"{error}"
        )
        return

    print("\nExport completed!")
    print(
        f"Total anime entries: "
        f"{total_anime_count}"
    )
    print(f"Output file: {output_path.name}")
    print(
        f"Saved to: "
        f"{output_path.resolve()}"
    )


if __name__ == "__main__":
    main()
