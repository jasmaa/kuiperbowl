import json
import urllib.request
import os
import lzma


def convert():
    """Convert PB json dump to fixture"""

    # Download archive
    print("Downloading archive...")
    urllib.request.urlretrieve(
        "https://github.com/jasmaa/database-dumps/raw/master/2017-04-11-QUIZBOWL.json.xz",
        "input.json.xz",
    )

    # Parse and convert
    print("Converting...")
    with lzma.open("input.json.xz") as f:
        output = []
        data = f.read().decode("utf-8").strip()
        for i, entry in enumerate(data.split("\n")):

            entry = json.loads(entry)
            # Only keep entries with curlies
            if (
                "answer" in entry
                and "{" in entry["answer"]
                and "}" in entry["answer"]
            ):
                output.append(
                    {
                        "model": "game.question",
                        "pk": i + 1,
                        "fields": {
                            "category": entry["category"],
                            "points": 20,
                            "content": entry["question"],
                            "answer": entry["answer"],
                            "difficulty": entry["difficulty"],
                            "duration": len(entry["question"]) / 30,
                        },
                    }
                )

    with open("./fixtures/pbdump.json", "w") as f:
        json.dump(output, f)
        print("Created fixtures/pbdump.json")

    # Remove archive
    os.remove("input.json.xz")


if __name__ == "__main__":
    convert()
