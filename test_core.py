from core.market_logic import MarketAnalyzer
import pandas as pd

def test_logic():
    print("Initializing MarketAnalyzer...")
    analyzer = MarketAnalyzer()
    
    print("Analyzing market status...")
    results = analyzer.analyze_market_status()
    
    if "error" in results:
        print(f"Error: {results['error']}")
        return

    print("\n--- Analysis Results ---")
    print(f"Date: {results['date']}")
    
    print(f"\n[Funding]: {results['funding']['status']} ({results['funding']['description']})")
    print(f"  Vol: {results['funding']['value']} vs MA20: {results['funding']['ma20']:.2f}")
    
    print(f"\n[Sentiment]: {results['sentiment']['status']} ({results['sentiment']['description']})")
    print(f"  Score: {results['sentiment']['score']:.2f}%")
    
    print(f"\n[Trend]: {results['trend']['status']}")
    print(f"  Price: {results['trend']['current_price']} vs EMA200: {results['trend']['ema200']:.2f}")
    
    print(f"\n[Timing]: {results['timing']['status']}")
    print(f"  Vol Rank: {results['timing']['volatility_rank']:.2f}")
    
    print(f"\n[Style]: {results['style']['suggestion']}")
    print(f"  Trend: {results['style']['trend']}")
    
    print("\nTest Complete.")

if __name__ == "__main__":
    test_logic()
