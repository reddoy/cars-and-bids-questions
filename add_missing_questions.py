#!/usr/bin/env python3
"""
Script to add missing questions from the template file to questions.csv
and update the HTML file with new stats.
"""

import csv
import re
import json

def timestamp_to_seconds(timestamp):
    """Convert timestamp string (HH:MM:SS or MM:SS) to seconds."""
    parts = timestamp.split(':')
    if len(parts) == 3:
        hours, minutes, seconds = map(int, parts)
        return hours * 3600 + minutes * 60 + seconds
    elif len(parts) == 2:
        minutes, seconds = map(int, parts)
        return minutes * 60 + seconds
    else:
        raise ValueError(f"Invalid timestamp format: {timestamp}")

def parse_template_file(template_file):
    """Parse the template file and extract questions."""
    questions = []
    
    with open(template_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    i = 0
    current_video_id = None
    current_video_title = None
    current_video_url = None
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Extract video info
        if line.startswith('Video ID:'):
            current_video_id = line.split('Video ID:')[1].strip()
        elif line.startswith('Title:'):
            current_video_title = line.split('Title:')[1].strip()
        elif line.startswith('URL:'):
            current_video_url = line.split('URL:')[1].strip()
        
        # Look for questions
        if line.startswith('Question ') and ':' in line:
            # Find the timestamp and question in the next few lines
            timestamp = None
            question_text = None
            
            # Look ahead for timestamp and question
            for j in range(i+1, min(i+5, len(lines))):
                next_line = lines[j].strip()
                if next_line.startswith('Timestamp:'):
                    timestamp = next_line.split('Timestamp:')[1].strip()
                elif next_line.startswith('Question:'):
                    question_text = next_line.split('Question:')[1].strip()
                    break
            
            if timestamp and question_text and current_video_id and current_video_title:
                try:
                    timestamp_seconds = timestamp_to_seconds(timestamp)
                    questions.append({
                        'video_id': current_video_id,
                        'video_title': current_video_title,
                        'video_url': current_video_url if current_video_url else f"https://www.youtube.com/watch?v={current_video_id}",
                        'timestamp': timestamp,
                        'timestamp_seconds': timestamp_seconds,
                        'question': question_text
                    })
                except ValueError as e:
                    print(f"Error parsing timestamp {timestamp}: {e}")
        
        i += 1
    
    return questions

def fix_spelling_errors(question_text):
    """Fix common spelling errors in questions."""
    fixes = {
        'percieved': 'perceived',
        'modications': 'modifications',
        'Carerra': 'Carrera',
        # Add more spelling fixes as needed
    }
    
    for wrong, correct in fixes.items():
        question_text = question_text.replace(wrong, correct)
    
    return question_text

def add_questions_to_csv(csv_file, new_questions):
    """Add new questions to the CSV file."""
    # Read existing questions
    existing_questions = []
    existing_keys = set()
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row['video_id'], row['timestamp_seconds'])
            existing_keys.add(key)
            existing_questions.append(row)
    
    # Add new questions (avoid duplicates)
    added_count = 0
    for q in new_questions:
        key = (q['video_id'], str(q['timestamp_seconds']))
        if key not in existing_keys:
            # Fix spelling errors
            q['question'] = fix_spelling_errors(q['question'])
            existing_questions.append(q)
            existing_keys.add(key)
            added_count += 1
        else:
            print(f"Question already exists: {q['question'][:50]}...")
    
    # Write back to CSV
    fieldnames = ['video_id', 'video_title', 'video_url', 'timestamp', 'timestamp_seconds', 'question']
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for q in existing_questions:
            writer.writerow(q)
    
    return added_count, len(existing_questions)

def update_html_stats(html_file, total_questions, total_videos):
    """Update the statistics in the HTML file."""
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Calculate average questions per video
    avg_per_video = round(total_questions / total_videos, 1) if total_videos > 0 else 0
    
    # Update stats in multiple places
    replacements = [
        (r'<span id="total-questions">\d+</span>', f'<span id="total-questions">{total_questions}</span>'),
        (r'<span id="total-videos">\d+</span>', f'<span id="total-videos">{total_videos}</span>'),
        (r'Showing <span id="results-count">\d+</span> of \d+ questions', f'Showing <span id="results-count">{total_questions}</span> of {total_questions} questions'),
        (r'<div class="stat-box-value">492</div>', f'<div class="stat-box-value">{total_questions}</div>'),
        (r'<div class="stat-box-value">86</div>\s*<div class="stat-box-label">Videos with Questions</div>', 
         f'<div class="stat-box-value">{total_videos}</div>\n                        <div class="stat-box-label">Videos with Questions</div>'),
        (r'<div class="stat-box-value">5\.7</div>', f'<div class="stat-box-value">{avg_per_video}</div>'),
    ]
    
    for pattern, replacement in replacements:
        html_content = re.sub(pattern, replacement, html_content)
    
    # Write back
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Updated HTML stats: {total_questions} questions, {total_videos} videos, {avg_per_video} avg per video")

def main():
    template_file = 'missing_videos_questions_template.txt'
    csv_file = 'questions.csv'
    html_file = 'questions_search.html'
    
    print("Parsing template file...")
    new_questions = parse_template_file(template_file)
    print(f"Found {len(new_questions)} questions in template")
    
    print("\nAdding questions to CSV...")
    added_count, total_questions = add_questions_to_csv(csv_file, new_questions)
    print(f"Added {added_count} new questions. Total questions: {total_questions}")
    
    # Count unique videos
    video_ids = set()
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            video_ids.add(row['video_id'])
    total_videos = len(video_ids)
    
    print(f"\nTotal unique videos: {total_videos}")
    
    print("\nUpdating HTML stats...")
    update_html_stats(html_file, total_questions, total_videos)
    
    print("\nDone!")

if __name__ == '__main__':
    main()

