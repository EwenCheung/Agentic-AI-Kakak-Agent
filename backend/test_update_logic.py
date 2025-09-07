#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agent.scheduler_agent.tools.calendar_tools import _is_time_only, _parse_time_to_24h

def test_time_logic():
    print("=== Testing Enhanced Update Logic ===")
    
    # Test time detection
    test_times = ['4pm', '16:00', '4:30pm', '2024-01-15T16:00:00', 'September 9th', 'tomorrow', '9am', '12:30pm']
    print('\n📅 Time-only detection:')
    for t in test_times:
        is_time = _is_time_only(t)
        print(f'  {t:<20} -> {is_time}')
    
    print('\n🕐 Time parsing to 24h:')
    time_only_examples = ['4pm', '16:00', '4:30pm', '9am', '12pm', '12am', '11:45pm', '1:15am']
    for t in time_only_examples:
        parsed = _parse_time_to_24h(t)
        print(f'  {t:<10} -> {parsed}')
    
    print("\n✅ Enhanced update logic test complete!")

if __name__ == "__main__":
    test_time_logic()
