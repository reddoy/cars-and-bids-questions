#!/usr/bin/env python3
"""
Script to update the embedded JavaScript questions array in the HTML file.
Reads from questions.csv and optionally questions_with_transcriptions.csv.
"""

import csv
import json
import re

def update_html_questions_array(html_file, csv_file, transcriptions_file=None):
    """Update the JavaScript questions array in the HTML file."""
    
    # Read transcriptions if available
    transcriptions = {}
    if transcriptions_file:
        try:
            with open(transcriptions_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    key = (row['video_id'], row['timestamp_seconds'])
                    if row.get('transcription'):
                        transcriptions[key] = row['transcription']
        except FileNotFoundError:
            print(f"Transcriptions file not found: {transcriptions_file}")
    
    # Read questions from CSV
    questions = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row['video_id'], row['timestamp_seconds'])
            question_obj = {
                'video_id': row['video_id'],
                'video_title': row['video_title'],
                'video_url': row['video_url'],
                'timestamp': row['timestamp'],
                'timestamp_seconds': row['timestamp_seconds'],
                'question': row['question']
            }
            # Add transcription if available
            if key in transcriptions:
                question_obj['transcription'] = transcriptions[key]
            
            questions.append(question_obj)
    
    # Read HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Generate JavaScript array
    js_array = json.dumps(questions, indent=8, ensure_ascii=False)
    
    # Replace the questions array in the HTML
    # The array is on a single line, so we'll find the line and replace it
    lines = html_content.split('\n')
    
    # Find the line with "const questions = ["
    line_idx = None
    for i, line in enumerate(lines):
        if 'const questions = [' in line:
            line_idx = i
            break
    
    if line_idx is None:
        print("Could not find 'const questions = [' in HTML")
        return False
    
    # Replace that line
    lines[line_idx] = '        const questions = ' + js_array + ';'
    new_html = '\n'.join(lines)
    
    # Write back
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(new_html)
    
    print(f"Updated HTML with {len(questions)} questions")
    return True

if __name__ == '__main__':
    html_file = 'questions_search.html'
    csv_file = 'questions.csv'
    transcriptions_file = 'questions_with_transcriptions.csv'
    
    update_html_questions_array(html_file, csv_file, transcriptions_file)

