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
    # Find the start of the array
    start_marker = '        const questions = ['
    start_pos = html_content.find(start_marker)
    
    if start_pos == -1:
        print("Could not find 'const questions = [' in HTML")
        return False
    
    # Find the end of the array by looking for the closing ]; 
    # We need to find the matching closing bracket
    # Start searching after the opening bracket
    search_start = start_pos + len(start_marker)
    bracket_count = 1  # We already found the opening [
    end_pos = None
    
    for i in range(search_start, len(html_content)):
        if html_content[i] == '[':
            bracket_count += 1
        elif html_content[i] == ']':
            bracket_count -= 1
            if bracket_count == 0:
                # Found the closing bracket, check for semicolon
                if i + 1 < len(html_content) and html_content[i + 1] == ';':
                    end_pos = i + 2
                    break
                elif i + 1 < len(html_content):
                    # Might be on next line, check a bit further
                    next_chars = html_content[i+1:i+10].strip()
                    if next_chars.startswith(';'):
                        end_pos = i + 1 + next_chars.find(';') + 1
                        break
    
    if end_pos is None:
        print("Could not find end of questions array")
        return False
    
    # Replace the entire array
    replacement = '        const questions = ' + js_array + ';'
    new_html = html_content[:start_pos] + replacement + html_content[end_pos:]
    
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

