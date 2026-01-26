#!/usr/bin/env python3
"""
Calculate question statistics including longest/shortest questions
"""

import csv
import json
import re
from collections import Counter

def calculate_question_stats(csv_file):
    """Calculate statistics about questions"""
    questions = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            questions.append({
                'video_id': row['video_id'],
                'video_title': row['video_title'],
                'video_url': row['video_url'],
                'timestamp': row['timestamp'],
                'timestamp_seconds': row['timestamp_seconds'],
                'question': row['question']
            })
    
    # Find longest and shortest questions
    longest_q = max(questions, key=lambda x: len(x['question']))
    shortest_q = min(questions, key=lambda x: len(x['question']))
    
    # Find video with minimum questions
    from collections import defaultdict
    questions_by_video = defaultdict(list)
    for q in questions:
        questions_by_video[q['video_id']].append(q)
    
    min_questions_video = min(questions_by_video.items(), key=lambda x: len(x[1]))
    
    # Calculate top words (excluding stop words and names)
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 
        'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'you', 'your', 'what', 'when', 'where', 'why', 
        'how', 'which', 'who', 'this', 'that', 'these', 'those', 'it', 'its', 'they', 'them',
        'we', 'our', 'he', 'she', 'his', 'her', 'him', 'i', 'my', 'me', 'if', 'than', 'then',
        'about', 'into', 'onto', 'from', 'by', 'as', 'so', 'up', 'down', 'out', 'off', 'over',
        'under', 'again', 'further', 'once', 'here', 'there', 'when', 'where', 'why', 'how',
        'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
        'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'can', 'cannot'
    }
    
    # Common names to exclude
    names = {'doug', 'kennan', 'kennan\'s', 'filippo', 'nick', 'demuro', 'doug\'s'}
    
    # Extract words from all questions
    all_words = []
    for q in questions:
        question_text = q['question'].lower()
        # Remove punctuation and split
        words = re.findall(r'\b[a-z]+\b', question_text)
        # Filter out stop words, names, and short words
        words = [w for w in words if w not in stop_words and w not in names and len(w) > 3]
        all_words.extend(words)
    
    # Count word frequency
    word_counts = Counter(all_words)
    top_words = word_counts.most_common(10)
    
    stats = {
        'longest_question': {
            'question': longest_q['question'],
            'length': len(longest_q['question']),
            'video_title': longest_q['video_title'],
            'video_url': longest_q['video_url'],
            'timestamp': longest_q['timestamp'],
            'timestamp_seconds': longest_q['timestamp_seconds']
        },
        'shortest_question': {
            'question': shortest_q['question'],
            'length': len(shortest_q['question']),
            'video_title': shortest_q['video_title'],
            'video_url': shortest_q['video_url'],
            'timestamp': shortest_q['timestamp'],
            'timestamp_seconds': shortest_q['timestamp_seconds']
        },
        'min_questions_video': {
            'video_id': min_questions_video[0],
            'video_title': min_questions_video[1][0]['video_title'],
            'video_url': min_questions_video[1][0]['video_url'],
            'question_count': len(min_questions_video[1])
        },
        'top_words': top_words
    }
    
    return stats

if __name__ == '__main__':
    stats = calculate_question_stats('questions.csv')
    print(json.dumps(stats, indent=2))

