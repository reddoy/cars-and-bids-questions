# Cars & Bids Questions

A searchable archive of every community question answered on [THIS CAR POD](https://www.youtube.com/playlist?list=PLRsapyZqDs1oR-egCLXRK-qmdPIZf1y5-), the Cars & Bids podcast. Each question links straight to the timestamp in the episode where it's answered.

**Live:** [reddoy.github.io/cars-and-bids-questions](https://reddoy.github.io/cars-and-bids-questions/)

**Status:** Fan project, not affiliated with Cars & Bids.

## Background

I love watching the Cars & Bids podcast, so I gathered every community question in one place. You can look up a question and jump straight to how the hosts answered it.

## Features

- Search 560+ questions across every episode
- Jump to the exact moment each question is answered on YouTube
- Questions grouped into categories (car brands, rankings and comparisons, personal questions, and more)
- Stats on question counts and how long answers run

## Tech stack

- A static site in a single HTML page with vanilla JavaScript, hosted on GitHub Pages
- Python scripts that pull data from the YouTube Data API v3

## How the data is built

Each script reads and writes files in the repo root:

| Step | Script | Reads | Writes |
|---|---|---|---|
| 1 | `get_youtube_descriptions.py` | The podcast playlist | `youtube_descriptions.json` |
| 2 | `extract_questions.py` | `youtube_descriptions.json` | `questions.csv`, parsed from each episode's "Community Questions" timestamps |
| 3 | `add_missing_questions.py` | `missing_videos_questions_template.txt` | `questions.csv`, for episodes without timestamps in the description |
| 4 | `update_html_questions.py` | `questions.csv` | The question list in `questions_search.html` |
| 5 | `update_html_stats.py` | `questions.csv` | The stats section in `questions_search.html` |

Helper scripts:

- `check_playlist.py` compares the playlist against what's already fetched.
- `calculate_question_stats.py` and `calculate_answer_durations_fixed.py` print stats.

`index.html` is the page GitHub Pages serves.

## Getting started

```bash
pip install -r requirements.txt
export YOUTUBE_API_KEY=your_key   # from Google Cloud Console with YouTube Data API v3 enabled

python get_youtube_descriptions.py --playlist "https://www.youtube.com/playlist?list=PLRsapyZqDs1oR-egCLXRK-qmdPIZf1y5-"
python extract_questions.py --input youtube_descriptions.json --output questions.csv
python update_html_questions.py
python update_html_stats.py
```

`get_youtube_descriptions.py` also accepts `--input video_ids.txt` for specific videos and `--format json|txt|csv`. Run any script with `--help` to see its options.

API quota: fetching a video costs 1 unit, and each playlist page of 50 videos costs 1 more. The default quota is 10,000 units per day.

## Deploying

See [`DEPLOY.md`](DEPLOY.md). The site is served by GitHub Pages from the `main` branch.
