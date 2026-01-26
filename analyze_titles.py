#!/usr/bin/env python3
"""
Analyze video titles to create filter categories.
"""

import csv
import re
from collections import Counter, defaultdict

def analyze_titles(csv_file):
    """Analyze video titles and create categories."""
    
    # Read all unique videos with their data
    videos = {}
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            video_id = row['video_id']
            if video_id not in videos:
                videos[video_id] = {
                    'title': row['video_title'],
                    'video_id': video_id,
                    'video_url': row['video_url']
                }
    
    print(f"Analyzing {len(videos)} unique videos...\n")
    
    # Define category patterns
    categories = {
        'Car Brands': {
            'keywords': ['BMW', 'Porsche', 'Ferrari', 'Lamborghini', 'Mercedes', 'Audi', 'Tesla', 
                        'Toyota', 'Honda', 'Ford', 'Chevrolet', 'Corvette', 'Mustang', 'Nissan',
                        'Maserati', 'Bentley', 'Rolls', 'McLaren', 'Aston Martin', 'Lexus',
                        'Subaru', 'Mazda', 'Volkswagen', 'VW', 'Jaguar', 'Land Rover', 'Range Rover'],
            'matches': []
        },
        'Rankings & Lists': {
            'keywords': ['Rank', 'Ranked', 'Best', 'Worst', 'Top', 'Every', 'All', 'List'],
            'matches': []
        },
        'Money & Market': {
            'keywords': ['Price', 'Cost', 'Market', 'Deal', 'Value', 'Worth', 'Sell', 'Buy', 
                        'Auction', 'Bids', 'Money', 'Cheap', 'Expensive', 'Bargain'],
            'matches': []
        },
        'New & Reveals': {
            'keywords': ['New', 'Revealed', 'Unveiled', 'Announced', 'Coming', 'Incoming', 
                        'Teased', 'Spotted', 'Leaked'],
            'matches': []
        },
        'Questions & Discussions': {
            'keywords': ['Why', 'What', 'How', 'When', 'Where', 'Who', 'Should', 'Would', 
                        'Can', 'Is', 'Are', 'Does', 'Do', '?'],
            'matches': []
        },
        'Failures & Problems': {
            'keywords': ['Fail', 'Failing', 'Dead', 'Killed', 'Gone', 'Discontinued', 
                        'Trouble', 'Problem', 'Issue', 'Scam'],
            'matches': []
        },
        'Electric & EV': {
            'keywords': ['Electric', 'EV', 'Hybrid', 'Battery', 'Charging', 'Tesla'],
            'matches': []
        },
        'Supercars & Exotics': {
            'keywords': ['Supercar', 'Hypercar', 'Exotic', 'Ferrari', 'Lamborghini', 
                        'McLaren', 'Bugatti', 'Koenigsegg'],
            'matches': []
        }
    }
    
    # Analyze each video
    for video_id, video_data in videos.items():
        title = video_data['title'].upper()
        
        for category, data in categories.items():
            for keyword in data['keywords']:
                if keyword.upper() in title:
                    if video_id not in [m['video_id'] for m in data['matches']]:
                        data['matches'].append({
                            'video_id': video_id,
                            'title': video_data['title']
                        })
                    break
    
    # Print results
    print("Category Analysis:\n")
    for category, data in categories.items():
        count = len(data['matches'])
        percentage = (count / len(videos)) * 100
        print(f"{category}: {count} videos ({percentage:.1f}%)")
        if count > 0 and count <= 5:
            for match in data['matches']:
                print(f"  - {match['title'][:60]}...")
        print()
    
    return categories, videos

if __name__ == '__main__':
    categories, videos = analyze_titles('questions.csv')
    
    # Save categories to JSON for use in HTML
    import json
    output = {
        'categories': {},
        'videos': videos
    }
    
    for category, data in categories.items():
        output['categories'][category] = [m['video_id'] for m in data['matches']]
    
    with open('title_categories.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print("✅ Saved categories to title_categories.json")





