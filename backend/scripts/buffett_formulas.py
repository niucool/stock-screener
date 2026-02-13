#!/usr/bin/env python
"""
Warren Buffett's 10 Investment Formulas Implementation
Based on Berkshire Hathaway's investment criteria and Buffett's letters to shareholders.
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

class FormulaStatus(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"

@dataclass
class FormulaResult:
    """Result of a single Buffett formula evaluation."""
    name: str
    description: str
    status: FormulaStatus
    value: Optional[float] = None
    target: Optional[float] = None
    details: Optional[str] = None
    
    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'status': self.status.value,
            'value': self.value,
            'target': self.target,
            'details': self.details
        }

class BuffettFormulaEngine:
    """
    Evaluates stocks using Warren Buffett's 10 investment formulas.
    Each formula returns PASS/FAIL/INSUFFICIENT_DATA based on financial data.
    """
    
    def __init__(self, financial_facts: Dict[str, Any]):
        """
        Initialize with financial facts extracted from SEC data.
        
        Expected financial_facts structure:
        {
            'Assets': float,
            'CurrentAssets': float,
            'Liabilities': float,
            'CurrentLiabilities': float,
            'LongTermDebt': float,
            'TotalDebt': float,
            'Equity': float,
            'CashAndEquivalents': float,
            'ShortTermInvestments': float,
            'Revenue': float,
            'OperatingIncome': float,
            'NetIncome': float,
            'InterestExpense': float,
            'OperatingCashFlow': float,
            'FreeCashFlow': float,
            'CapitalExpenditures': float,
            'SharesOutstanding': float
        }
        """
        self.facts = financial_facts
        
    def evaluate_all(self) -> List[FormulaResult]:
        """Evaluate all 10 Buffett formulas."""
        formulas = [
            self.cash_test,
            self.debt_to_equity,
            self.free_cash_flow_to_debt,
            self.return_on_equity,
            self.current_ratio,
            self.operating_margin,
            self.asset_turnover,
            self.interest_coverage,
            self.earnings_stability,
            self.capital_allocation
        ]
        
        results = []
        for formula in formulas:
            try:
                result = formula()
                results.append(result)
            except Exception as e:
                logging.error(f"Error evaluating formula {formula.__name__}: {e}")
                results.append(FormulaResult(
                    name=formula.__name__,
                    description="Error evaluating formula",
                    status=FormulaStatus.INSUFFICIENT_DATA,
                    details=str(e)
                ))
        
        return results
    
    def cash_test(self) -> FormulaResult:
        """
        Formula 1: Cash Test
        Cash + Short-Term Investments > Total Debt
        Buffett wants companies that can pay off all debt with cash on hand.
        """
        cash = self.facts.get('CashAndEquivalents', 0)
        short_term_inv = self.facts.get('ShortTermInvestments', 0)
        total_debt = self.facts.get('TotalDebt', 0)
        
        if total_debt == 0:
            # No debt is excellent
            ratio = float('inf')
        else:
            ratio = (cash + short_term_inv) / total_debt
        
        target = 1.0  # Cash should cover 100% of debt
        status = FormulaStatus.PASS if ratio > target else FormulaStatus.FAIL
        
        return FormulaResult(
            name="Cash Test",
            description="Cash + Short-Term Investments > Total Debt",
            status=status,
            value=ratio,
            target=target,
            details=f"Cash/Investments: ${cash + short_term_inv:,.0f}, Debt: ${total_debt:,.0f}, Ratio: {ratio:.2f}x"
        )
    
    def debt_to_equity(self) -> FormulaResult:
        """
        Formula 2: Debt-to-Equity Ratio
        Total Liabilities / Equity < 0.5
        Buffett prefers companies with conservative leverage.
        """
        liabilities = self.facts.get('Liabilities', 0)
        equity = self.facts.get('Equity', 0)
        
        if equity <= 0:
            ratio = float('inf')
        else:
            ratio = liabilities / equity
        
        target = 0.5  # Maximum 0.5x debt-to-equity
        status = FormulaStatus.PASS if ratio < target else FormulaStatus.FAIL
        
        return FormulaResult(
            name="Debt-to-Equity",
            description="Total Liabilities / Equity < 0.5",
            status=status,
            value=ratio,
            target=target,
            details=f"Liabilities: ${liabilities:,.0f}, Equity: ${equity:,.0f}, Ratio: {ratio:.2f}"
        )
    
    def free_cash_flow_to_debt(self) -> FormulaResult:
        """
        Formula 3: Free Cash Flow to Debt
        Free Cash Flow / Total Debt > 0.25
        Measures ability to pay down debt from operations.
        """
        free_cash_flow = self.facts.get('FreeCashFlow', 0)
        total_debt = self.facts.get('TotalDebt', 0)
        
        if total_debt == 0:
            ratio = float('inf')
        else:
            ratio = free_cash_flow / total_debt
        
        target = 0.25  # FCF should cover 25% of debt annually
        status = FormulaStatus.PASS if ratio > target else FormulaStatus.FAIL
        
        return FormulaResult(
            name="Free Cash Flow to Debt",
            description="Free Cash Flow / Total Debt > 0.25",
            status=status,
            value=ratio,
            target=target,
            details=f"FCF: ${free_cash_flow:,.0f}, Debt: ${total_debt:,.0f}, Ratio: {ratio:.2f}"
        )
    
    def return_on_equity(self) -> FormulaResult:
        """
        Formula 4: Return on Equity (ROE)
        Net Income / Equity > 15%
        Measures profitability relative to shareholder equity.
        """
        net_income = self.facts.get('NetIncome', 0)
        equity = self.facts.get('Equity', 0)
        
        if equity <= 0:
            roe = 0
        else:
            roe = (net_income / equity) * 100  # Convert to percentage
        
        target = 15.0  # Minimum 15% ROE
        status = FormulaStatus.PASS if roe > target else FormulaStatus.FAIL
        
        return FormulaResult(
            name="Return on Equity",
            description="Net Income / Equity > 15%",
            status=status,
            value=roe,
            target=target,
            details=f"Net Income: ${net_income:,.0f}, Equity: ${equity:,.0f}, ROE: {roe:.1f}%"
        )
    
    def current_ratio(self) -> FormulaResult:
        """
        Formula 5: Current Ratio
        Current Assets / Current Liabilities > 1.5
        Measures short-term liquidity.
        """
        current_assets = self.facts.get('CurrentAssets', 0)
        current_liabilities = self.facts.get('CurrentLiabilities', 0)
        
        if current_liabilities == 0:
            ratio = float('inf')
        else:
            ratio = current_assets / current_liabilities
        
        target = 1.5  # Minimum 1.5x current ratio
        status = FormulaStatus.PASS if ratio > target else FormulaStatus.FAIL
        
        return FormulaResult(
            name="Current Ratio",
            description="Current Assets / Current Liabilities > 1.5",
            status=status,
            value=ratio,
            target=target,
            details=f"Current Assets: ${current_assets:,.0f}, Current Liabilities: ${current_liabilities:,.0f}, Ratio: {ratio:.2f}x"
        )
    
    def operating_margin(self) -> FormulaResult:
        """
        Formula 6: Operating Margin
        Operating Profit / Revenue > 12%
        Measures operational efficiency and pricing power.
        """
        operating_income = self.facts.get('OperatingIncome', 0)
        revenue = self.facts.get('Revenue', 0)
        
        if revenue == 0:
            margin = 0
        else:
            margin = (operating_income / revenue) * 100  # Convert to percentage
        
        target = 12.0  # Minimum 12% operating margin
        status = FormulaStatus.PASS if margin > target else FormulaStatus.FAIL
        
        return FormulaResult(
            name="Operating Margin",
            description="Operating Profit / Revenue > 12%",
            status=status,
            value=margin,
            target=target,
            details=f"Operating Income: ${operating_income:,.0f}, Revenue: ${revenue:,.0f}, Margin: {margin:.1f}%"
        )
    
    def asset_turnover(self) -> FormulaResult:
        """
        Formula 7: Asset Turnover
        Revenue / Total Assets > 0.5
        Measures efficiency of asset utilization.
        """
        revenue = self.facts.get('Revenue', 0)
        assets = self.facts.get('Assets', 0)
        
        if assets == 0:
            turnover = 0
        else:
            turnover = revenue / assets
        
        target = 0.5  # Minimum 0.5x asset turnover
        status = FormulaStatus.PASS if turnover > target else FormulaStatus.FAIL
        
        return FormulaResult(
            name="Asset Turnover",
            description="Revenue / Total Assets > 0.5",
            status=status,
            value=turnover,
            target=target,
            details=f"Revenue: ${revenue:,.0f}, Assets: ${assets:,.0f}, Turnover: {turnover:.2f}x"
        )
    
    def interest_coverage(self) -> FormulaResult:
        """
        Formula 8: Interest Coverage
        Operating Profit / Interest Expense > 3×
        Measures ability to service debt from operations.
        """
        operating_income = self.facts.get('OperatingIncome', 0)
        interest_expense = self.facts.get('InterestExpense', 0)
        
        if interest_expense == 0:
            coverage = float('inf')
        else:
            coverage = operating_income / interest_expense
        
        target = 3.0  # Minimum 3x interest coverage
        status = FormulaStatus.PASS if coverage > target else FormulaStatus.FAIL
        
        return FormulaResult(
            name="Interest Coverage",
            description="Operating Profit / Interest Expense > 3×",
            status=status,
            value=coverage,
            target=target,
            details=f"Operating Income: ${operating_income:,.0f}, Interest Expense: ${interest_expense:,.0f}, Coverage: {coverage:.1f}x"
        )
    
    def earnings_stability(self) -> FormulaResult:
        """
        Formula 9: Earnings Stability
        Positive earnings 8+ of last 10 years
        Note: This requires historical data. For single-year analysis,
        we check if current earnings are positive.
        """
        net_income = self.facts.get('NetIncome', 0)
        
        # For single-year analysis, just check if earnings are positive
        # In a full implementation, we would check 10 years of data
        is_positive = net_income > 0
        
        status = FormulaStatus.PASS if is_positive else FormulaStatus.FAIL
        
        return FormulaResult(
            name="Earnings Stability",
            description="Positive earnings (current year)",
            status=status,
            value=1.0 if is_positive else 0.0,
            target=1.0,
            details=f"Current Net Income: ${net_income:,.0f} ({'Positive' if is_positive else 'Negative'})"
        )
    
    def capital_allocation(self) -> FormulaResult:
        """
        Formula 10: Capital Allocation
        ROE > 15% (same as Formula 4, but as a value creation check)
        This is Buffett's way of checking if management creates value.
        """
        # Reuse ROE calculation
        net_income = self.facts.get('NetIncome', 0)
        equity = self.facts.get('Equity', 0)
        
        if equity <= 0:
            roe = 0
        else:
            roe = (net_income / equity) * 100
        
        target = 15.0  # Same as ROE target
        status = FormulaStatus.PASS if roe > target else FormulaStatus.FAIL
        
        return FormulaResult(
            name="Capital Allocation",
            description="ROE > 15% (value creation)",
            status=status,
            value=roe,
            target=target,
            details=f"ROE: {roe:.1f}% - Management {'creates' if roe > target else 'destroys'} value"
        )


def test_buffett_formulas():
    """Test the Buffett formula engine with sample data."""
    
    # Sample financial data for Apple (simplified)
    sample_facts = {
        'Assets': 352_755_000_000,
        'CurrentAssets': 143_566_000_000,
        'Liabilities': 279_414_000_000,
        'CurrentLiabilities': 145_308_000_000,
        'LongTermDebt': 95_277_000_000,
        'TotalDebt': 111_087_000_000,
        'Equity': 73_341_000_000,
        'CashAndEquivalents': 48_351_000_000,
        'ShortTermInvestments': 31_495_000_000,
        'Revenue': 383_285_000_000,
        'OperatingIncome': 114_301_000_000,
        'NetIncome': 96_995_000_000,
        'InterestExpense': 2_931_000_000,
        'OperatingCashFlow': 110_543_000_000,
        'FreeCashFlow': 99_584_000_000,
        'CapitalExpenditures': 10_959_000_000,
        'SharesOutstanding': 15_550_000_000
    }
    
    print("Testing Buffett Formulas with Apple (AAPL) data...")
    print("=" * 80)
    
    engine = BuffettFormulaEngine(sample_facts)
    results = engine.evaluate_all()
    
    pass_count = sum(1 for r in results if r.status == FormulaStatus.PASS)
    fail_count = sum(1 for r in results if r.status == FormulaStatus.FAIL)
    insufficient_count = sum(1 for r in results if r.status == FormulaStatus.INSUFFICIENT_DATA)
    
    print(f"\nOverall Score: {pass_count}/10 formulas passed")
    print(f"Pass: {pass_count}, Fail: {fail_count}, Insufficient Data: {insufficient_count}")
    print("=" * 80)
    
    for result in results:
        status_icon = "✅" if result.status == FormulaStatus.PASS else "❌" if result.status == FormulaStatus.FAIL else "⚠️"
        print(f"\n{status_icon} {result.name}")
        print(f"  {result.description}")
        print(f"  Status: {result.status.value}")
        if result.value is not None:
            print(f"  Value: {result.value:.2f} (Target: >{result.target})")
        if result.details:
            print(f"  Details: {result.details}")
    
    print("\n" + "=" * 80)
    print("Interpretation:")
    print(f"- {pass_count}/10 formulas passed: ", end="")
    
    if pass_count >= 8:
        print("EXCELLENT QUALITY - Buffett would approve!")
    elif pass_count >= 6:
        print("GOOD QUALITY - Solid investment")
    elif pass_count >= 4:
        print("AVERAGE QUALITY - Needs careful analysis")
    else:
        print("POOR QUALITY - High risk, avoid")


if __name__ == "__main__":
    test_buffett_formulas()