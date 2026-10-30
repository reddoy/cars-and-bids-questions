"""Update the THIS CAR POD question archive.

Finds new episodes in the podcast playlist, pulls the community questions out
of each episode's description, cuts the hosts' answer to each question out of
YouTube's captions, sorts the questions into categories, and writes the files
the web app loads.

Usage:
    pip install -r pipeline/requirements.txt
    python3 pipeline/update.py                      # add anything new
    python3 pipeline/update.py --retry-transcripts  # also retry answers that had no captions

Set YOUTUBE_API_KEY to look up episodes with the YouTube Data API instead of
yt-dlp. GitHub Actions needs it, because YouTube blocks scraping from cloud
servers.
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from categorize import categorize  # noqa: E402
from extract import extract_questions  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
APP_DATA_DIR = ROOT / "web" / "public" / "data"

PLAYLIST_ID = "PLRsapyZqDs1oR-egCLXRK-qmdPIZf1y5-"
API = "https://www.googleapis.com/youtube/v3"
MAX_ANSWER_SECONDS = 20 * 60
CHAPTER_LINE = re.compile(r"^\s*(\d{1,2}:\d{2}(?::\d{2})?)\s")
NOISE = re.compile(r"\[(music|applause|__)\]", re.IGNORECASE)
# Chapter titles in the Q&A section that aren't questions.
NOT_A_QUESTION = re.compile(r"^(&\s*)?(all the )?(questions?|answers?)(\s*(&|and)\s*answers?)?\W*$|^car news\b", re.IGNORECASE)


def load(name, default):
    path = DATA_DIR / name
    return json.loads(path.read_text()) if path.exists() else default


def save(directory, name, data, indent=1):
    directory.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, indent=indent, ensure_ascii=False) if indent else json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    (directory / name).write_text(text + "\n")


def to_seconds(stamp):
    seconds = 0
    for part in stamp.split(":"):
        seconds = seconds * 60 + int(part)
    return seconds


def episode_number(title):
    match = re.search(r"(?:\bEP\.?\s?|#|CAR\s?POD!?\s+)(\d+)\s*$", title, re.IGNORECASE) or re.search(r"\bEP\.?\s?(\d+)", title, re.IGNORECASE)
    return int(match.group(1)) if match else None


def fill_episode_numbers(episodes):
    """Number episodes whose title has no number, when the episodes either side of it do."""
    ordered = sorted(episodes, key=lambda e: e["published"])
    for before, episode, after in zip(ordered, ordered[1:], ordered[2:]):
        if episode["number"] is None and before["number"] and after and after["number"] == before["number"] + 2:
            episode["number"] = before["number"] + 1


def is_question(text, t, episode):
    return not NOT_A_QUESTION.match(text.strip()) and t < (episode.get("duration") or float("inf"))


# Episode lookups


def playlist_with_api(key):
    """Video IDs in the playlist, plus title, date, length and description for each."""
    ids, token = [], None
    while True:
        params = {"part": "contentDetails", "playlistId": PLAYLIST_ID, "maxResults": 50, "key": key}
        if token:
            params["pageToken"] = token
        page = requests.get(f"{API}/playlistItems", params=params, timeout=30).json()
        ids += [item["contentDetails"]["videoId"] for item in page["items"]]
        token = page.get("nextPageToken")
        if not token:
            break

    videos = {}
    for i in range(0, len(ids), 50):
        params = {"part": "snippet,contentDetails", "id": ",".join(ids[i : i + 50]), "key": key}
        for item in requests.get(f"{API}/videos", params=params, timeout=30).json()["items"]:
            iso = item["contentDetails"]["duration"]
            h, m, s = (int(x or 0) for x in re.fullmatch(r"P(?:\d+D)?T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso).groups())
            videos[item["id"]] = {
                "title": item["snippet"]["title"],
                "published": item["snippet"]["publishedAt"][:10],
                "duration": h * 3600 + m * 60 + s,
                "description": item["snippet"]["description"],
            }
    return [video_id for video_id in ids if video_id in videos], videos


def playlist_with_ytdlp(known):
    """Same as playlist_with_api, but only fetches full details for videos not in `known`."""
    import yt_dlp

    options = {"quiet": True, "no_warnings": True, "skip_download": True}
    with yt_dlp.YoutubeDL({**options, "extract_flat": "in_playlist"}) as ydl:
        listing = ydl.extract_info(f"https://www.youtube.com/playlist?list={PLAYLIST_ID}", download=False)
    entries = [e for e in listing["entries"] if e.get("title") not in ("[Private video]", "[Deleted video]")]

    videos = {}
    with yt_dlp.YoutubeDL(options) as ydl:
        for entry in entries:
            if entry["id"] in known:
                videos[entry["id"]] = {"duration": entry.get("duration")}
                continue
            try:
                info = ydl.extract_info(f"https://www.youtube.com/watch?v={entry['id']}", download=False, process=False)
            except yt_dlp.utils.DownloadError as error:
                print(f"  skipping {entry['id']}: {error}")
                continue
            date = info.get("upload_date") or ""
            videos[entry["id"]] = {
                "title": info["title"],
                "published": f"{date[:4]}-{date[4:6]}-{date[6:]}",
                "duration": info.get("duration"),
                "description": info.get("description") or "",
            }
    return [e["id"] for e in entries if e["id"] in videos], videos


# Answers


def chapter_starts(description):
    return sorted({to_seconds(m.group(1)) for line in description.splitlines() if (m := CHAPTER_LINE.match(line))})


def answer_end(question, episode):
    later = [s for s in chapter_starts(episode["description"]) if s > question["t"]]
    end = min(later) if later else (episode.get("duration") or question["t"] + MAX_ANSWER_SECONDS)
    return max(min(end, question["t"] + MAX_ANSWER_SECONDS), question["t"] + 1)


def clean_transcript(pieces):
    text = " ".join(piece.replace("\n", " ") for piece in pieces)
    text = NOISE.sub("", text)
    turns = [re.sub(r"\s+", " ", turn).strip() for turn in text.split(">>")]
    return "\n".join(turn for turn in turns if turn)


class Blocked(Exception):
    pass


def fetch_answers(video_id, questions, episode):
    """Answer transcript for each question in one episode. Raises Blocked if YouTube blocks us."""
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import CouldNotRetrieveTranscript, IpBlocked, RequestBlocked

    try:
        snippets = YouTubeTranscriptApi().fetch(video_id, languages=["en"]).snippets
    except (RequestBlocked, IpBlocked) as error:
        raise Blocked(type(error).__name__) from error
    except CouldNotRetrieveTranscript:
        return {q["id"]: None for q in questions}

    answers = {}
    for q in questions:
        end = answer_end(q, episode)
        text = clean_transcript(s.text for s in snippets if q["t"] <= s.start < end)
        answers[q["id"]] = text or None
    return answers


# Main


def update(retry_transcripts=False, skip_transcripts=False, delay=5):
    episodes = {e["id"]: e for e in load("episodes.json", [])}
    questions = load("questions.json", [])
    transcripts = load("transcripts.json", {})

    key = os.environ.get("YOUTUBE_API_KEY")
    print("Checking the playlist" + (" with the YouTube API" if key else " with yt-dlp") + "...")
    order, videos = playlist_with_api(key) if key else playlist_with_ytdlp(episodes)

    new_ids = [video_id for video_id in order if video_id not in episodes]
    for video_id in order:
        if video_id in episodes:
            if videos[video_id].get("duration"):
                episodes[video_id]["duration"] = videos[video_id]["duration"]
            continue
        video = videos[video_id]
        episodes[video_id] = {"id": video_id, "number": episode_number(video["title"]), **video}

    known = {q["id"] for q in questions}
    added = 0
    for video_id in new_ids:
        for found in extract_questions(episodes[video_id]["description"]):
            qid = f"{video_id}-{found['timestamp_seconds']}"
            if qid in known or not is_question(found["question"], found["timestamp_seconds"], episodes[video_id]):
                continue
            known.add(qid)
            questions.append(
                {"id": qid, "video": video_id, "t": found["timestamp_seconds"], "question": found["question"], "category": categorize(found["question"])}
            )
            added += 1
    print(f"  {len(new_ids)} new episodes, {added} new questions")

    if not skip_transcripts:
        wanted = [q for q in questions if q["id"] not in transcripts or (retry_transcripts and transcripts[q["id"]] is None)]
        by_video = {}
        for q in wanted:
            by_video.setdefault(q["video"], []).append(q)
        print(f"Fetching answers for {len(wanted)} questions across {len(by_video)} episodes...")
        for i, (video_id, video_questions) in enumerate(by_video.items(), 1):
            try:
                transcripts.update(fetch_answers(video_id, video_questions, episodes[video_id]))
            except Blocked as error:
                print(f"  YouTube blocked caption requests ({error}), stopping. Try again in an hour or two.")
                break
            print(f"  {i}/{len(by_video)} {episodes[video_id]['title'][:70]}")
            # YouTube starts refusing caption requests if they come too fast.
            time.sleep(delay)

    fill_episode_numbers(episodes.values())
    episode_list = sorted(episodes.values(), key=lambda e: e["published"], reverse=True)
    questions.sort(key=lambda q: (episodes[q["video"]]["published"], q["t"]), reverse=True)
    save(DATA_DIR, "episodes.json", episode_list)
    save(DATA_DIR, "questions.json", questions)
    save(DATA_DIR, "transcripts.json", dict(sorted(transcripts.items())))
    build_app_data(episode_list, questions, transcripts)
    return len(new_ids), added


def build_app_data(episode_list, questions, transcripts):
    """Slimmer copies of the data for the web app."""
    episodes = {e["id"]: e for e in episode_list}
    counts = {}
    for q in questions:
        counts[q["video"]] = counts.get(q["video"], 0) + 1

    save(
        APP_DATA_DIR,
        "episodes.json",
        [
            {k: e.get(k) for k in ("id", "number", "title", "published", "duration")} | {"questions": counts.get(e["id"], 0)}
            for e in episode_list
        ],
        indent=None,
    )
    save(
        APP_DATA_DIR,
        "questions.json",
        [
            {"id": q["id"], "video": q["video"], "t": q["t"], "end": answer_end(q, episodes[q["video"]]), "question": q["question"], "category": q["category"], "hasAnswer": bool(transcripts.get(q["id"]))}
            for q in questions
        ],
        indent=None,
    )
    save(APP_DATA_DIR, "transcripts.json", {k: v for k, v in sorted(transcripts.items()) if v}, indent=None)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--retry-transcripts", action="store_true", help="retry answers that had no captions last time")
    parser.add_argument("--skip-transcripts", action="store_true", help="don't fetch answer transcripts")
    parser.add_argument("--delay", type=float, default=5, help="seconds to wait between episodes when fetching captions (default 5)")
    args = parser.parse_args()
    new_episodes, new_questions = update(args.retry_transcripts, args.skip_transcripts, args.delay)
    print(f"Done: {new_episodes} new episodes, {new_questions} new questions.")


if __name__ == "__main__":
    main()
