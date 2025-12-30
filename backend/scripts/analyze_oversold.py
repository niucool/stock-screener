#!/usr/bin/env python3
"""
Oversold Stock Analysis with Risk Assessment
Categorizes oversold stocks into risk levels based on multiple technical indicators.
"""

import sqlite3
import pandas as pd

DB_PATH = '../data/stocks.db'

def analyze_oversold_stocks():
    """Analyze oversold stocks and categorize by risk level."""

    conn = sqlite3.connect(DB_PATH)

    # Query oversold stocks (Williams %R < -80)
    query = """
        SELECT
            symbol,
            close,
            williams_r_21,
            rsi_14,
            adx_14,
            price_vs_sma200_pct,
            pct_from_52w_high,
            pct_from_52w_low,
            bb_position,
            relative_volume,
            macd_hist,
            volume,
            hist_volatility_20
        FROM stock_indicators
        WHERE williams_r_21 < -80
        ORDER BY williams_r_21 ASC
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        print("No oversold stocks found (Williams %R < -80)")
        return

    # Scoring system for risk assessment
    def calculate_risk_score(row):
        """Calculate risk score (0-100, higher = riskier)"""
        score = 0

        # Williams %R extremity (0-20 points)
        if row['williams_r_21'] < -95:
            score += 20  # Extremely oversold (capitulation or falling knife)
        elif row['williams_r_21'] < -90:
            score += 15
        elif row['williams_r_21'] < -85:
            score += 10
        else:
            score += 5

        # RSI (0-20 points)
        if row['rsi_14'] < 25:
            score += 20  # Deep oversold (risky)
        elif row['rsi_14'] < 30:
            score += 15
        elif row['rsi_14'] < 35:
            score += 10
        elif row['rsi_14'] < 45:
            score += 5  # Mild oversold (better)
        else:
            score += 0  # Not oversold on RSI

        # Distance from 200-day SMA (0-20 points)
        if row['price_vs_sma200_pct'] < -20:
            score += 20  # Deep below long-term average
        elif row['price_vs_sma200_pct'] < -10:
            score += 15
        elif row['price_vs_sma200_pct'] < -5:
            score += 10
        elif row['price_vs_sma200_pct'] < 0:
            score += 5
        else:
            score += 0  # Above 200-day SMA (strong)

        # Distance from 52-week high (0-20 points)
        if row['pct_from_52w_high'] < -40:
            score += 20  # Far from highs
        elif row['pct_from_52w_high'] < -30:
            score += 15
        elif row['pct_from_52w_high'] < -20:
            score += 10
        elif row['pct_from_52w_high'] < -10:
            score += 5
        else:
            score += 0  # Near highs (strong)

        # ADX trend strength (0-20 points)
        if row['adx_14'] > 30:
            # Strong trend - check if downtrend
            if row['price_vs_sma200_pct'] < -5:
                score += 15  # Strong downtrend (risky)
            else:
                score -= 10  # Strong uptrend in pullback (good)
        elif row['adx_14'] > 20:
            score += 5  # Moderate trend
        else:
            score += 10  # Weak trend (choppy, risky)

        return min(max(score, 0), 100)  # Clamp to 0-100

    def assess_upside_potential(row):
        """Assess upside potential (0-100, higher = better)"""
        potential = 0

        # Distance from 52w low (more room = lower potential from here)
        if row['pct_from_52w_low'] < 10:
            potential += 25  # Near 52w low (potential for bounce)
        elif row['pct_from_52w_low'] < 20:
            potential += 20
        elif row['pct_from_52w_low'] < 40:
            potential += 10
        else:
            potential += 5

        # Bollinger Band position
        if row['bb_position'] < 5:
            potential += 20  # At lower BB (stretched)
        elif row['bb_position'] < 15:
            potential += 15
        elif row['bb_position'] < 25:
            potential += 10
        else:
            potential += 5

        # MACD Histogram (divergence potential)
        if row['macd_hist'] > 0:
            potential += 15  # Positive momentum divergence
        elif row['macd_hist'] > -1:
            potential += 10
        else:
            potential += 5

        # Above 200-day SMA (in uptrend)
        if row['price_vs_sma200_pct'] > 5:
            potential += 20  # Strong uptrend
        elif row['price_vs_sma200_pct'] > 0:
            potential += 15
        elif row['price_vs_sma200_pct'] > -5:
            potential += 10
        else:
            potential += 5

        # Relative volume (interest)
        if row['relative_volume'] > 1.5:
            potential += 10  # High volume (capitulation or accumulation)
        elif row['relative_volume'] > 1.0:
            potential += 5

        # Volatility (lower = more stable)
        if row['hist_volatility_20'] < 20:
            potential += 10  # Low volatility (stable)
        elif row['hist_volatility_20'] < 30:
            potential += 5

        return min(potential, 100)

    # Calculate scores
    df['risk_score'] = df.apply(calculate_risk_score, axis=1)
    df['upside_score'] = df.apply(assess_upside_potential, axis=1)

    # Categorize
    def categorize(row):
        if row['risk_score'] < 40 and row['upside_score'] > 50:
            return 'QUALITY_PULLBACK'
        elif row['risk_score'] > 60:
            return 'HIGH_RISK'
        elif row['upside_score'] > 60:
            return 'POTENTIAL_REVERSAL'
        elif row['risk_score'] < 50:
            return 'MODERATE_BUY'
        else:
            return 'AVOID'

    df['category'] = df.apply(categorize, axis=1)

    # Sort by category and risk score
    category_order = ['QUALITY_PULLBACK', 'POTENTIAL_REVERSAL', 'MODERATE_BUY', 'AVOID', 'HIGH_RISK']
    df['category_rank'] = df['category'].map({cat: i for i, cat in enumerate(category_order)})
    df = df.sort_values(['category_rank', 'risk_score', 'williams_r_21'])

    # Print results
    print("=" * 120)
    print("OVERSOLD STOCKS ANALYSIS - RISK & OPPORTUNITY ASSESSMENT")
    print("=" * 120)
    print(f"\nTotal oversold stocks (Williams %R < -80): {len(df)}")
    print(f"Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
    print()

    for category in category_order:
        cat_df = df[df['category'] == category]
        if cat_df.empty:
            continue

        # Category descriptions
        descriptions = {
            'QUALITY_PULLBACK': '🟢 QUALITY PULLBACK - Low Risk, High Potential (BUY CANDIDATES)',
            'POTENTIAL_REVERSAL': '🟡 POTENTIAL REVERSAL - Medium Risk, Good Potential (WATCH)',
            'MODERATE_BUY': '🟡 MODERATE BUY - Balanced Risk/Reward (WATCH)',
            'AVOID': '🟠 AVOID - High Risk, Low Potential',
            'HIGH_RISK': '🔴 HIGH RISK - Falling Knives (AVOID)'
        }

        print("-" * 120)
        print(f"{descriptions[category]}")
        print(f"Count: {len(cat_df)}")
        print("-" * 120)

        for _, row in cat_df.head(10).iterrows():
            print(f"\n{row['symbol']:6s} ${row['close']:7.2f}  |  Risk: {row['risk_score']:2.0f}/100  |  Upside: {row['upside_score']:2.0f}/100")
            print(f"  Williams %R: {row['williams_r_21']:6.1f}  RSI: {row['rsi_14']:5.1f}  ADX: {row['adx_14']:5.1f}")
            print(f"  vs 200-day: {row['price_vs_sma200_pct']:6.1f}%  |  52w High: {row['pct_from_52w_high']:6.1f}%  |  52w Low: {row['pct_from_52w_low']:6.1f}%")
            print(f"  BB Position: {row['bb_position']:5.1f}  |  MACD Hist: {row['macd_hist']:7.2f}  |  Vol: {row['relative_volume']:.2f}x")

        if len(cat_df) > 10:
            print(f"\n  ... and {len(cat_df) - 10} more")
        print()

    # Summary statistics
    print("=" * 120)
    print("SUMMARY")
    print("=" * 120)
    print(f"Quality Pullbacks: {len(df[df['category'] == 'QUALITY_PULLBACK'])}")
    print(f"Potential Reversals: {len(df[df['category'] == 'POTENTIAL_REVERSAL'])}")
    print(f"Moderate Buys: {len(df[df['category'] == 'MODERATE_BUY'])}")
    print(f"High Risk: {len(df[df['category'] == 'HIGH_RISK'])}")
    print(f"Avoid: {len(df[df['category'] == 'AVOID'])}")
    print()

    # Export top candidates
    quality = df[df['category'] == 'QUALITY_PULLBACK']['symbol'].tolist()
    potential = df[df['category'] == 'POTENTIAL_REVERSAL']['symbol'].tolist()

    print("TOP BUY CANDIDATES (Quality Pullbacks):")
    print(", ".join(quality[:10]) if quality else "None")
    print()

    print("WATCH LIST (Potential Reversals):")
    print(", ".join(potential[:10]) if potential else "None")
    print()

    print("=" * 120)

    return df

if __name__ == "__main__":
    analyze_oversold_stocks()
