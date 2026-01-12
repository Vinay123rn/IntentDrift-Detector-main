from src.drift_detector import IntentDriftDetector

def run_test():
    print("--- Testing Enhancements (Persistence=1, Threshold=0.30) ---")
    # Note: Default args are already updated in the class
    detector = IntentDriftDetector() 
    
    sequence = [
        # Test 1: Weaker Interest Signal (should be caught by lower threshold/new anchors)
        "I like football", 
        
        # Test 2: Drift to Comparison (Standard)
        "Which league is better?",
        
        # Test 3: Drift to Complaint (Standard)
        "This league is overrated",
        
        # Test 4: Unknown -> Known (Should NOT drift)
        "blah blah random noise", # Should be unknown
        "I will stop watching"    # Decision (Should be 'update', not 'drift' from unknown)
    ]
    
    print(f"{'Utterance':<30} | {'Detected':<15} | {'Drift?':<10} | {'Explanation'}")
    print("-" * 120)
    
    for utt in sequence:
        result = detector.update(utt)
        drift_status = "YES" if result["intent_drift"] else "NO"
        print(f"{utt:<30} | {result['detected_intent']:<15} | {drift_status:<10} | {result['explanation']}")

if __name__ == "__main__":
    run_test()
