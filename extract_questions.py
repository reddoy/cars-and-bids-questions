#!/usr/bin/env python3
"""
Extract timestamps and questions from YouTube video descriptions.

This script parses video descriptions to find the "Community Questions" section
and extracts all timestamps and questions that follow.
"""

import json
import re
import csv
import argparse


def parse_timestamp(timestamp_str):
    """Parse timestamp string (HH:MM:SS) and return seconds."""
    parts = timestamp_str.split(':')
    if len(parts) == 3:
        hours, minutes, seconds = map(int, parts)
        return hours * 3600 + minutes * 60 + seconds
    elif len(parts) == 2:
        minutes, seconds = map(int, parts)
        return minutes * 60 + seconds
    return 0


def extract_questions(description):
    """Extract timestamps and questions from description text."""
    if not description:
        return []
    
    questions = []
    lines = description.split('\n')
    
    # Find where "Chapters" or "CHAPTERS" section starts (case insensitive)
    # Also handle "CHAPTERS:" with colon
    chapters_start_idx = None
    for i, line in enumerate(lines):
        line_lower = line.strip().lower()
        # Check for various chapter header formats
        if (line_lower == 'chapters' or 
            line_lower == 'chapter' or 
            line_lower.startswith('chapters') or 
            line_lower.startswith('chapter') or
            line_lower == 'chapters:' or
            'chapters:' in line_lower):
            chapters_start_idx = i + 1
            break
    
    # If no chapters header found, look for timestamp patterns directly
    # This handles cases where timestamps start without a header
    if chapters_start_idx is None:
        # Look for the first line that matches a timestamp pattern
        timestamp_pattern = re.compile(r'^(\d{1,2}:\d{2}:\d{2}|\d{1,2}:\d{2})\s+')
        for i, line in enumerate(lines):
            if timestamp_pattern.match(line.strip()):
                chapters_start_idx = i
                break
    
    if chapters_start_idx is None:
        return []
    
    # Parse timestamp and question pairs from the chapters section
    # Pattern: HH:MM:SS Question text (with optional HH:MM format)
    # Also handle formats like "Intro- 0:00" or "Q&A- 58:57"
    timestamp_pattern = re.compile(r'^(\d{1,2}:\d{2}:\d{2}|\d{1,2}:\d{2})\s+(.+)$')
    timestamp_pattern_alt = re.compile(r'^(.+?)\s*-\s*(\d{1,2}:\d{2}:\d{2}|\d{1,2}:\d{2})$')
    
    # First pass: find where Q&A section starts (if it exists)
    timestamp_pattern = re.compile(r'^(\d{1,2}:\d{2}:\d{2}|\d{1,2}:\d{2})\s+(.+)$')
    qa_section_start_seconds = None
    section_headers = ['community questions', 'q&a', 'questions', 'question time', 'community q&a']
    
    for line in lines[chapters_start_idx:]:
        line = line.strip()
        if not line:
            continue
        match = timestamp_pattern.match(line)
        if match:
            timestamp = match.group(1)
            question_text = match.group(2).strip().lower()
            # Check if this line contains a Q&A section header
            if any(header in question_text for header in section_headers):
                qa_section_start_seconds = parse_timestamp(timestamp)
                break
        # Also check standalone headers
        line_lower = line.lower()
        is_section_header = any(header in line_lower for header in section_headers) and len(line_lower.split()) <= 3
        if is_section_header:
            # For standalone headers, we need to check the next line for timestamp
            # But for now, we'll handle this in the main loop
            pass
    
    # Track if we're in a Q&A section
    in_qa_section = False
    qa_section_exists = qa_section_start_seconds is not None
    
    for line in lines[chapters_start_idx:]:
        line = line.strip()
        if not line:
            continue
        
        # Stop if we hit the end markers (hashtags, separator lines, etc.)
        if line.startswith('#') or (line.startswith('http') and '://' in line) or line.startswith('='):
            break
        
        # Check if we're entering a Q&A section
        line_lower = line.lower()
        
        # Check if this is a standalone section header (3 or fewer words)
        is_section_header = any(header in line_lower for header in section_headers) and len(line_lower.split()) <= 3
        
        # Try standard format: timestamp followed by text
        match = timestamp_pattern.match(line)
        if match:
            timestamp = match.group(1)
            question_text = match.group(2).strip()
            question_text_lower = question_text.lower()
            
            # Check if the text portion contains Q&A indicators (like "00:47:25 Community Q&A!")
            # If it does, mark that we're in Q&A section
            if any(header in question_text_lower for header in section_headers):
                in_qa_section = True
                qa_section_exists = True
                # Try to extract the actual question by removing Q&A header text
                # For example: "Community Q&A! Buy the BZ4X..." -> "Buy the BZ4X..."
                for header in section_headers:
                    if header in question_text_lower:
                        # Find where the header ends
                        header_idx = question_text_lower.find(header)
                        # Get text after the header
                        after_header = question_text[header_idx + len(header):].strip()
                        # Remove leading punctuation like "!" or ":" 
                        after_header = after_header.lstrip('!?:. ').strip()
                        if after_header:
                            # Use the text after the header as the question
                            question_text = after_header
                            question_text_lower = question_text.lower()
                        else:
                            # If there's no text after the header, skip this line as it's just a header
                            continue
                        break
            
            # Extract if it contains a question mark OR if we're in Q&A section
            # But exclude section headers and end markers
            if question_text:
                exclude_patterns = ['community questions', 'q&a', 'final thoughts', 'outro', 'closing', 'community q&a']
                # Also exclude if text is just "questions" followed by optional punctuation
                is_excluded = any(pattern in question_text_lower for pattern in exclude_patterns)
                # Check if it's just "questions" with optional punctuation (like "Questions!", "Questions!!", etc.)
                if not is_excluded and question_text_lower.strip().rstrip('!?.:').strip() == 'questions':
                    is_excluded = True
                
                # If a Q&A section exists in this video, only extract from within that section
                # Otherwise, extract entries with question marks as a fallback
                should_extract = False
                if qa_section_exists:
                    # Only extract if timestamp is at or after Q&A section start
                    timestamp_seconds = parse_timestamp(timestamp)
                    should_extract = timestamp_seconds >= qa_section_start_seconds
                else:
                    # No Q&A section detected, extract entries with question marks
                    should_extract = '?' in question_text
                
                if not is_excluded and should_extract:
                    questions.append({
                        'timestamp': timestamp,
                        'timestamp_seconds': parse_timestamp(timestamp),
                        'question': question_text
                    })
        
        # Check standalone section headers (not on timestamp lines)
        if is_section_header:
            in_qa_section = True
            qa_section_exists = True
            # Don't include section headers as questions, just mark that we're in Q&A
            continue
        
        # Check if we're leaving Q&A section (Final Thoughts, Outro, etc.)
        if in_qa_section:
            end_markers = ['final thoughts', 'outro', 'closing', 'wrap up', 'conclusion']
            if any(marker in line_lower for marker in end_markers):
                in_qa_section = False
                continue
        
        # Try alternative format: text - timestamp (like "Q&A- 58:57")
        if not match:
            match_alt = timestamp_pattern_alt.match(line)
            if match_alt:
                question_text = match_alt.group(1).strip()
                timestamp = match_alt.group(2)
                question_text_lower = question_text.lower()
                
                # Check if the text portion contains Q&A indicators
                if any(header in question_text_lower for header in section_headers):
                    in_qa_section = True
                    # Skip the header line itself, but mark that we're in Q&A
                    continue
                
                # Extract if it contains a question mark OR if we're in Q&A section
                # But exclude section headers and end markers
                if question_text:
                    exclude_patterns = ['community questions', 'q&a', 'final thoughts', 'outro', 'closing', 'community q&a']
                    is_excluded = any(pattern in question_text_lower for pattern in exclude_patterns)
                    # Check if it's just "questions" with optional punctuation (like "Questions!", "Questions!!", etc.)
                    if not is_excluded and question_text_lower.strip().rstrip('!?.:').strip() == 'questions':
                        is_excluded = True
                    
                    # If a Q&A section exists in this video, only extract from within that section
                    # Otherwise, extract entries with question marks as a fallback
                    should_extract = False
                    if qa_section_exists:
                        # Only extract if timestamp is at or after Q&A section start
                        timestamp_seconds = parse_timestamp(timestamp)
                        should_extract = timestamp_seconds >= qa_section_start_seconds
                    else:
                        # No Q&A section detected, extract entries with question marks
                        should_extract = '?' in question_text
                    
                    if not is_excluded and should_extract:
                        questions.append({
                            'timestamp': timestamp,
                            'timestamp_seconds': parse_timestamp(timestamp),
                            'question': question_text
                        })
    
    return questions


def process_videos(input_file, output_file):
    """Process video descriptions and extract questions."""
    # Read JSON file
    print(f"Reading video descriptions from {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        videos = json.load(f)
    
    print(f"Processing {len(videos)} videos...")
    
    # Extract questions from each video
    all_questions = []
    videos_without_questions = []
    
    for video in videos:
        video_id = video['video_id']
        title = video['title']
        description = video.get('description', '')
        url = video.get('url', '')
        
        questions = extract_questions(description)
        
        if questions:
            for q in questions:
                all_questions.append({
                    'video_id': video_id,
                    'video_title': title,
                    'video_url': url,
                    'timestamp': q['timestamp'],
                    'timestamp_seconds': q['timestamp_seconds'],
                    'question': q['question']
                })
        else:
            videos_without_questions.append(title)
    
    # Write to CSV
    print(f"\nFound {len(all_questions)} questions from {len(videos) - len(videos_without_questions)} videos")
    
    if videos_without_questions:
        print(f"Note: {len(videos_without_questions)} videos had no chapters section or no questions ending with '?' found")
    
    print(f"Writing results to {output_file}...")
    
    fieldnames = ['video_id', 'video_title', 'video_url', 'timestamp', 'timestamp_seconds', 'question']
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_questions)
    
    print(f"Successfully wrote {len(all_questions)} questions to {output_file}")
    
    return len(all_questions), len(videos_without_questions)


def main():
    parser = argparse.ArgumentParser(
        description='Extract timestamps and questions from YouTube video descriptions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python extract_questions.py --input youtube_descriptions.json --output questions.csv
        """
    )
    
    parser.add_argument('--input', '-i',
                       help='Input JSON file with video descriptions (default: youtube_descriptions.json)',
                       default='youtube_descriptions.json')
    parser.add_argument('--output', '-o',
                       help='Output CSV file (default: questions.csv)',
                       default='questions.csv')
    
    args = parser.parse_args()
    
    try:
        count, missing = process_videos(args.input, args.output)
        print(f"\nSummary:")
        print(f"  Total questions extracted: {count}")
        print(f"  Videos without chapters/questions: {missing}")
    except FileNotFoundError as e:
        print(f"Error: File not found: {e}")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON file: {e}")
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == '__main__':
    main()

