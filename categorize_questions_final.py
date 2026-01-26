#!/usr/bin/env python3
"""
Create 4-5 really specific, meaningful categories.
"""

import csv
import json
from collections import defaultdict

def categorize_question(question):
    """Categorize a question - 4-5 really specific categories."""
    question_lower = question.lower()
    
    # 1. Money/Value/Buying - very specific
    if any(word in question_lower for word in ['price', 'cost', 'worth', 'value', 'expensive', 
                                               'cheap', 'deal', 'money', 'buy', 'sell', 'market',
                                               'finance', 'paid', 'million', 'thousand', '$',
                                               'reserve', 'auction', 'bids', 'budget', 'afford',
                                               'investment', 'retain', 'depreciate', 'appreciate',
                                               'how much', 'what price', 'what cost']):
        return ['💰 Money & Value']
    
    # 2. Personal questions about Doug/team - very specific
    if any(word in question_lower for word in ['doug', 'nick', 'filippo', 'kennan', 
                                               'your car', 'your garage', 'you own', 'you bought',
                                               'you review', 'you think', 'you want', 'you get',
                                               'you have', 'you drive', 'you daily', 'you would',
                                               'you should', 'you prefer', 'your favorite',
                                               'your opinion', 'your take', 'your thoughts',
                                               'have you', 'did you', 'do you', 'are you',
                                               'would you', 'should you', 'can you',
                                               'what do you', 'what would you', 'what did you',
                                               'how do you', 'how did you', 'how would you',
                                               'why did you', 'why do you', 'why would you',
                                               'when did you', 'when do you', 'when will you',
                                               'your collection', 'your fleet', 'your cars']):
        return ['👤 Personal Questions']
    
    # 3. Rankings & Comparisons - specific pattern
    if any(word in question_lower for word in ['rank', 'ranking', 'best', 'worst', 'better', 
                                               'vs', 'versus', 'compare', 'comparison', 'prefer',
                                               'favorite', 'top', 'which is', 'which car',
                                               'which would', 'which has', 'which should',
                                               'most', 'least', 'better than', 'worse than',
                                               'holy trinity', 'rank the']):
        return ['📊 Rankings & Comparisons']
    
    # 4. Car brand specific - when brand is the main focus
    if any(brand in question_lower for brand in ['bmw', 'porsche', 'ferrari', 'lamborghini', 
                                                 'mercedes', 'audi', 'tesla', 'toyota', 'honda',
                                                 'ford', 'corvette', 'mustang', 'nissan',
                                                 'maserati', 'bentley', 'mclaren', 'aston',
                                                 'lexus', 'subaru', 'mazda', 'vw', 'jaguar',
                                                 'land rover', 'genesis', 'hyundai', 'kia',
                                                 'lucid', 'rivian', 'fisker', 'cadillac',
                                                 'infiniti', 'acura', 'volvo', 'lincoln',
                                                 'alfa romeo', 'jeep', 'dodge', 'chrysler',
                                                 'mini', 'fiat', 'alfa', 'bentayga', 'urus',
                                                 'countach', 'enzo', 'carrera gt', 'm5', 'm3',
                                                 '911', 'cayenne', 'g-wagon', 'g-wagen',
                                                 'model s', 'model 3', 'cybertruck', 'taycan',
                                                 'r8', 'gt-r', 'supra', 'sti', 'wrx']):
        return ['🚗 Car Brands']
    
    # 5. Future/Predictions - specific time-based questions
    if any(word in question_lower for word in ['will', 'future', 'coming', 'new', 'next', 
                                               'predict', 'expect', 'ever', 'going to',
                                               'when will', 'what will', 'would be',
                                               'should get', 'coming out', 'be released',
                                               'be popular', 'become', 'be successful',
                                               'incoming', 'teased', 'revealed', 'announced']):
        return ['🔮 Future & Predictions']
    
    # Everything else - catch opinion/thought questions and merge with Personal
    if any(word in question_lower for word in ['think', 'thoughts', 'opinion', 'feel', 
                                                'believe', 'consider', 'view', 'take']):
        # If it mentions "you" or names, it's personal, otherwise it's about cars in general
        if any(word in question_lower for word in ['you', 'your', 'doug', 'nick', 'filippo', 'kennan']):
            return ['👤 Personal Questions']
        # Otherwise it's a general opinion question about cars
        return ['📝 General']
    
    # Otherwise General
    return ['📝 General']

def main():
    print("Creating final refined categories...\n")
    
    questions = []
    with open('questions.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            questions.append({
                'video_id': row['video_id'],
                'question': row['question'],
                'timestamp_seconds': int(row['timestamp_seconds'])
            })
    
    print(f"Analyzing {len(questions)} questions...\n")
    
    # Categorize all questions
    question_to_categories = {}
    category_counts = defaultdict(int)
    
    for q in questions:
        question = q['question']
        categories = categorize_question(question)
        question_to_categories[question] = categories
        for cat in categories:
            category_counts[cat] += 1
    
    # Define emojis for each category (5 main categories)
    category_emojis = {
        '💰 Money & Value': '💰',
        '👤 Personal Questions': '👤',
        '📊 Rankings & Comparisons': '📊',
        '🚗 Car Brands': '🚗',
        '🔮 Future & Predictions': '🔮',
        '📝 General': '📝'
    }
    
    # Print results
    print("Category Analysis:\n")
    sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
    for category, count in sorted_categories:
        emoji = category_emojis.get(category, '📌')
        percentage = (count / len(questions)) * 100
        print(f"{emoji} {category}: {count} questions ({percentage:.1f}%)")
    
    # Create mapping: question -> categories
    question_categories = {}
    for q in questions:
        question = q['question']
        question_categories[question] = question_to_categories[question]
    
    # Save to JSON
    output = {
        'question_categories': question_categories,
        'category_emojis': category_emojis,
        'category_counts': dict(category_counts)
    }
    
    with open('question_categories.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved {len(category_emojis)} categories to question_categories.json")

if __name__ == '__main__':
    main()

