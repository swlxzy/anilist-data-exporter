import json
import urllib.request
import urllib.error
import os
import re


API_URL = "https://graphql.anilist.co"


def safe_filename(name):
    """Dosya isminde sorun çıkarabilecek karakterleri temizler."""
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = name.strip()
    return name or "list"


def unique_filename(folder, filename):
    """Aynı dosya varsa üzerine yazmak yerine _2, _3... ekler."""
    base, ext = os.path.splitext(filename)
    path = os.path.join(folder, filename)

    counter = 2

    while os.path.exists(path):
        path = os.path.join(folder, f"{base}_{counter}{ext}")
        counter += 1

    return path


def graphql_request(query, variables):
    payload = json.dumps({
        "query": query,
        "variables": variables
    }).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "AniListExporter/1.0"
    }

    request = urllib.request.Request(
        API_URL,
        data=payload,
        headers=headers
    )

    try:
        with urllib.request.urlopen(request) as response:
            data = json.loads(response.read().decode("utf-8"))

        if "errors" in data:
            print("AniList GraphQL hatası:")
            for error in data["errors"]:
                print(" -", error.get("message", "Bilinmeyen hata"))
            return None

        return data

    except urllib.error.HTTPError as e:
        print(f"HTTP hatası: {e.code}")
        return None

    except urllib.error.URLError as e:
        print(f"Bağlantı hatası: {e.reason}")
        return None

    except Exception as e:
        print(f"Beklenmeyen hata: {e}")
        return None


def get_lists(username):
    query = '''
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
    '''

    data = graphql_request(
        query,
        {"username": username}
    )

    if not data:
        return None

    return (
        data
        .get("data", {})
        .get("MediaListCollection", {})
        .get("lists", [])
    )


def process_entry(entry):
    media = entry.get("media", {})

    media_id = media.get("id")

    titles = media.get("title", {})
    title = titles.get("english") or titles.get("romaji")

    if not media_id or not title:
        return None

    item = {
        "title": title
    }

    # Kullanıcının verdiği genel puan
    user_score = entry.get("score")

    if user_score is not None and user_score > 0:
        item["score"] = user_score

    # AniList topluluk ortalaması
    average = media.get("averageScore")

    if average is not None and average > 0:
        item["average"] = average

    # Advanced Scores
    raw_advanced = entry.get("advancedScores")

    if isinstance(raw_advanced, dict):
        valid_advanced = {}
        empty_count = 0

        for category, score in raw_advanced.items():

            # 0 = değerlendirilmemiş
            if score == 0 or score is None:
                empty_count += 1
            else:
                valid_advanced[category.lower()] = score

        if valid_advanced:
            item["advanced"] = valid_advanced

        if empty_count > 0:
            item["emptyAdvanced"] = empty_count

    return media_id, item


def main():
    username = input("AniList username: ").strip()

    if not username:
        print("Kullanıcı adı boş olamaz!")
        return

    print("\nHesabınızdaki listeler:\n")

    lists = get_lists(username)

    if not lists:
        print("Liste bulunamadı veya profil gizli!")
        return

    available_lists = []

    for index, anime_list in enumerate(lists, start=1):

        name = anime_list.get("name", "Unnamed")
        count = len(anime_list.get("entries", []))

        available_lists.append(anime_list)

        print(f"[{index}] {name} ({count})")

    select_all_number = len(available_lists) + 1

    print(
        f"[{select_all_number}] HEPSİNİ ÇEK / SELECT ALL"
    )

    choice = input(
        "\nÇekilecek listeler "
        "(Örn: 1 veya 2,1,3): "
    ).strip()

    if not choice:
        print("Seçim yapılmadı!")
        return

    selected_numbers = []

    for part in choice.split(","):

        part = part.strip()

        if part.isdigit():

            number = int(part)

            if number not in selected_numbers:
                selected_numbers.append(number)

    if not selected_numbers:
        print("Geçersiz seçim!")
        return

    # SELECT ALL
    if select_all_number in selected_numbers:

        selected_lists = available_lists

    else:

        selected_lists = []

        for number in selected_numbers:

            if 1 <= number <= len(available_lists):

                anime_list = available_lists[number - 1]

                if anime_list not in selected_lists:
                    selected_lists.append(anime_list)

    if not selected_lists:
        print("Geçerli bir liste seçilmedi!")
        return

    # Kullanıcıya özel klasör
    output_folder = safe_filename(username)

    os.makedirs(output_folder, exist_ok=True)

    result_lists = {}
    summary_counts = {}

    total_count = 0

    # Her seçilen liste kendi içinde duplicate kontrolü yapar.
    # Böylece aynı anime iki farklı listede varsa ikisinde de kalabilir.
    for anime_list in selected_lists:

        list_name = anime_list.get("name", "Unnamed")
        entries = anime_list.get("entries", [])

        processed_entries = []
        seen_ids = set()

        for entry in entries:

            result = process_entry(entry)

            if not result:
                continue

            media_id, item = result

            if media_id in seen_ids:
                continue

            seen_ids.add(media_id)

            processed_entries.append(item)

        if processed_entries:

            result_lists[list_name] = processed_entries
            summary_counts[list_name] = len(processed_entries)
            total_count += len(processed_entries)

    # SELECT ALL ise kısa dosya adı
    if select_all_number in selected_numbers:

        base_filename = "select_all.json"

    else:

        # Seçilen listelerin isimlerinden dosya adı oluştur
        names = [
            safe_filename(anime_list.get("name", "list"))
            for anime_list in selected_lists
        ]

        base_filename = "_".join(names) + ".json"

    output_path = unique_filename(
        output_folder,
        base_filename
    )

    final_output = {
        "summary": {
            "total": total_count,
            "lists": summary_counts
        },
        "lists": result_lists
    }

    compressed_json = json.dumps(
        final_output,
        separators=(",", ":"),
        ensure_ascii=False
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(compressed_json)

    print("\n✅ İşlem tamamlandı!")
    print(f"📊 Toplam: {total_count} anime")
    print(f"📂 Dosya: {output_path}")


if __name__ == "__main__":
    main()