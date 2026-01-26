#!/usr/bin/env python3
"""
Update HTML with calculated statistics
"""

import csv
import re
from collections import defaultdict

def format_time(seconds):
    """Format seconds into MM:SS or HH:MM:SS"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"

def calculate_stats(csv_file):
    """Calculate all statistics from questions CSV"""
    questions = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            questions.append({
                'video_id': row['video_id'],
                'video_title': row['video_title'],
                'timestamp_seconds': int(row['timestamp_seconds']),
                'timestamp': row['timestamp'],
                'question': row['question']
            })
    
    # Group questions by video
    questions_by_video = defaultdict(list)
    for q in questions:
        questions_by_video[q['video_id']].append(q)
    
    # Calculate time gaps between questions in same video
    gaps = []
    for video_id, video_questions in questions_by_video.items():
        sorted_questions = sorted(video_questions, key=lambda x: x['timestamp_seconds'])
        for i in range(len(sorted_questions) - 1):
            gap = sorted_questions[i + 1]['timestamp_seconds'] - sorted_questions[i]['timestamp_seconds']
            if gap > 0:
                gaps.append(gap)
    
    # Calculate average question timestamp
    avg_timestamp_seconds = sum(q['timestamp_seconds'] for q in questions) / len(questions)
    
    # Questions per video
    questions_per_video = [len(video_questions) for video_questions in questions_by_video.values()]
    
    # Find video with most questions
    max_q_video = max(questions_by_video.items(), key=lambda x: len(x[1]))
    
    # Calculate questions per hour (estimate)
    estimated_video_length = 5400  # 90 minutes
    questions_per_hour = (len(questions) / len(questions_by_video)) * (3600 / estimated_video_length)
    
    stats = {
        'total_questions': len(questions),
        'total_videos': len(questions_by_video),
        'avg_questions_per_video': round(sum(questions_per_video) / len(questions_per_video), 1),
        'max_questions_in_video': max(questions_per_video) if questions_per_video else 0,
        'min_questions_in_video': min(questions_per_video) if questions_per_video else 0,
        'avg_time_between_questions_formatted': format_time(int(sum(gaps) / len(gaps))) if gaps else "0:00",
        'longest_gap_formatted': format_time(max(gaps)) if gaps else "0:00",
        'shortest_gap_formatted': format_time(min(gaps)) if gaps else "0:00",
        'avg_question_timestamp_formatted': format_time(int(avg_timestamp_seconds)),
        'video_with_most_questions_title': max_q_video[1][0]['video_title'][:30] + "..." if len(max_q_video[1][0]['video_title']) > 30 else max_q_video[1][0]['video_title'],
        'estimated_questions_per_hour': round(questions_per_hour, 1)
    }
    
    return stats

def update_html_stats(html_file, stats):
    """Update statistics in HTML file"""
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Update basic stats
    replacements = [
        (r'<div class="stat-box-value">535</div>\s*<div class="stat-box-label">Questions Answered</div>',
         f'<div class="stat-box-value">{stats["total_questions"]}</div>\n                        <div class="stat-box-label">Questions Answered</div>'),
        (r'<div class="stat-box-value">94</div>\s*<div class="stat-box-label">Videos with Questions</div>',
         f'<div class="stat-box-value">{stats["total_videos"]}</div>\n                        <div class="stat-box-label">Videos with Questions</div>'),
        (r'<div class="stat-box-value">5\.7</div>\s*<div class="stat-box-label">Questions per Video</div>',
         f'<div class="stat-box-value">{stats["avg_questions_per_video"]}</div>\n                        <div class="stat-box-label">Questions per Video</div>'),
        
        # Update timing stats
        (r'<div class="stat-box-value">5:06</div>\s*<div class="stat-box-label">Average Gap</div>',
         f'<div class="stat-box-value">{stats["avg_time_between_questions_formatted"]}</div>\n                        <div class="stat-box-label">Average Gap</div>'),
        (r'<div class="stat-box-value">55:58</div>\s*<div class="stat-box-label">Between Questions</div>',
         f'<div class="stat-box-value">{stats["longest_gap_formatted"]}</div>\n                        <div class="stat-box-label">Between Questions</div>'),
        (r'<div class="stat-box-value">0:09</div>\s*<div class="stat-box-label">Between Questions</div>',
         f'<div class="stat-box-value">{stats["shortest_gap_formatted"]}</div>\n                        <div class="stat-box-label">Between Questions</div>'),
        (r'<div class="stat-box-value">58:01</div>\s*<div class="stat-box-label">Into Video</div>',
         f'<div class="stat-box-value">{stats["avg_question_timestamp_formatted"]}</div>\n                        <div class="stat-box-label">Into Video</div>'),
        
        # Update record holders
        (r'<div class="stat-box-value">19</div>\s*<div class="stat-box-label">In One Video</div>',
         f'<div class="stat-box-value">{stats["max_questions_in_video"]}</div>\n                        <div class="stat-box-label">In One Video</div>'),
        (r'<div class="stat-box-value">3\.8</div>\s*<div class="stat-box-label">Estimated Rate</div>',
         f'<div class="stat-box-value">{stats["estimated_questions_per_hour"]}</div>\n                        <div class="stat-box-label">Estimated Rate</div>'),
        (r'<div class="stat-box-value">19</div>\s*<div class="stat-box-label">Holiday Special EP40</div>',
         f'<div class="stat-box-value">{stats["max_questions_in_video"]}</div>\n                        <div class="stat-box-label">{stats["video_with_most_questions_title"]}</div>'),
        (r'<div class="stat-box-value">1</div>\s*<div class="stat-box-label">Minimum Questions</div>',
         f'<div class="stat-box-value">{stats["min_questions_in_video"]}</div>\n                        <div class="stat-box-label">Minimum Questions</div>'),
    ]
    
    for pattern, replacement in replacements:
        html_content = re.sub(pattern, replacement, html_content)
    
    # Update results count
    html_content = re.sub(
        r'Showing <span id="results-count">\d+</span> of \d+ questions',
        f'Showing <span id="results-count">{stats["total_questions"]}</span> of {stats["total_questions"]} questions',
        html_content
    )
    
    # Update header stats
    html_content = re.sub(
        r'<span id="total-questions">\d+</span>',
        f'<span id="total-questions">{stats["total_questions"]}</span>',
        html_content
    )
    html_content = re.sub(
        r'<span id="total-videos">\d+</span>',
        f'<span id="total-videos">{stats["total_videos"]}</span>',
        html_content
    )
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Updated HTML stats:")
    print(f"  Total Questions: {stats['total_questions']}")
    print(f"  Total Videos: {stats['total_videos']}")
    print(f"  Avg per Video: {stats['avg_questions_per_video']}")
    print(f"  Avg Time Between Questions: {stats['avg_time_between_questions_formatted']}")
    print(f"  Avg Question Time: {stats['avg_question_timestamp_formatted']}")

if __name__ == '__main__':
    stats = calculate_stats('questions.csv')
    update_html_stats('questions_search.html', stats)

