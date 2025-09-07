#!/usr/bin/env python3

import re

def _is_time_only(time_str: str) -> bool:
    """Check if the input is just a time (like '4pm', '16:00') rather than a full datetime."""
    time_patterns = [
        r'^\d{1,2}:\d{2}\s*(am|pm)$',   # 4:30pm
        r'^\d{1,2}\s*(am|pm)$',         # 4pm
        r'^\d{1,2}:\d{2}$',             # 16:30
        r'^\d{1,2}$',                   # 16
    ]
    time_str_clean = time_str.lower().strip()
    return any(re.match(pattern, time_str_clean) for pattern in time_patterns)

def _parse_time_to_24h(time_str: str) -> str:
    """Convert time string to 24-hour format HH:MM."""
    time_str_clean = time_str.lower().strip()
    
    # 4:30pm -> 16:30
    match = re.match(r'^(\d{1,2}):(\d{2})\s*(am|pm)$', time_str_clean)
    if match:
        hour, minute, period = int(match.group(1)), int(match.group(2)), match.group(3)
        if period == 'pm' and hour != 12:
            hour += 12
        elif period == 'am' and hour == 12:
            hour = 0
        return f"{hour:02d}:{minute:02d}:00"
    
    # 4pm -> 16:00
    match = re.match(r'^(\d{1,2})\s*(am|pm)$', time_str_clean)
    if match:
        hour, period = int(match.group(1)), match.group(2)
        if period == 'pm' and hour != 12:
            hour += 12
        elif period == 'am' and hour == 12:
            hour = 0
        return f"{hour:02d}:00:00"
    
    # 16:30 -> 16:30:00
    match = re.match(r'^(\d{1,2}):(\d{2})$', time_str_clean)
    if match:
        hour, minute = int(match.group(1)), int(match.group(2))
        return f"{hour:02d}:{minute:02d}:00"
    
    # 16 -> 16:00:00
    match = re.match(r'^(\d{1,2})$', time_str_clean)
    if match:
        hour = int(match.group(1))
        return f"{hour:02d}:00:00"
    
    return "12:00:00"  # Default fallback

def test_time_logic():
    print("=== Testing Enhanced Update Logic ===")
    
    # Test time detection
    test_times = ['4pm', '16:00', '4:30pm', '2024-01-15T16:00:00', 'September 9th', 'tomorrow', '9am', '12:30pm']
    print('\n📅 Time-only detection:')
    for t in test_times:
        is_time = _is_time_only(t)
        status = "✅ TIME" if is_time else "❌ NOT TIME"
        print(f'  {t:<20} -> {status}')
    
    print('\n🕐 Time parsing to 24h:')
    time_only_examples = ['4pm', '16:00', '4:30pm', '9am', '12pm', '12am', '11:45pm', '1:15am']
    for t in time_only_examples:
        parsed = _parse_time_to_24h(t)
        print(f'  {t:<10} -> {parsed}')
    
    print("\n✅ Enhanced update logic test complete!")

if __name__ == "__main__":
    test_time_logic()
