"""
Report Generation and Analysis Utilities for TradeGenius AI
Includes CSV export, correlation heatmaps, stress testing, and ESG analysis
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger('tradegenius.utils')

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    logger.warning("Plotly not installed - visualization features disabled")


def export_analysis_to_csv(analysis_data: dict, symbol: str) -> str:
    """
    Export analysis results to CSV format.

    Args:
        analysis_data: Analysis dictionary from generate_ai_analysis
        symbol: Stock symbol

    Returns:
        CSV content as string
    """
    try:
        rows = []

        # Basic info
        row = {'Symbol': symbol, 'Metric': 'Current Price', 'Value': analysis_data.get('current_price', 'N/A')}
        rows.append(row)

        # Technical score
        tech_score = analysis_data.get('technical_score', {})
        row = {'Symbol': symbol, 'Metric': 'Technical Score', 'Value': tech_score.get('score', 'N/A')}
        rows.append(row)
        row = {'Symbol': symbol, 'Metric': 'Technical Grade', 'Value': tech_score.get('grade', 'N/A')}
        rows.append(row)

        # ML Ensemble
        ml_ensemble = analysis_data.get('ml_ensemble', {})
        row = {'Symbol': symbol, 'Metric': 'ML Prediction', 'Value': ml_ensemble.get('ensemble_prediction', 'N/A')}
        rows.append(row)
        row = {'Symbol': symbol, 'Metric': 'ML Confidence', 'Value': ml_ensemble.get('ensemble_confidence', 'N/A')}
        rows.append(row)
        row = {'Symbol': symbol, 'Metric': 'Prediction Horizon', 'Value': ml_ensemble.get('prediction_horizon', 'N/A')}
        rows.append(row)

        # Market regime
        regime = analysis_data.get('market_regime', {})
        row = {'Symbol': symbol, 'Metric': 'Market Regime', 'Value': regime.get('primary_regime', 'N/A')}
        rows.append(row)
        row = {'Symbol': symbol, 'Metric': 'Risk Level', 'Value': regime.get('risk_level', 'N/A')}
        rows.append(row)

        # AI Recommendation
        rec = analysis_data.get('ai_recommendation', {})
        row = {'Symbol': symbol, 'Metric': 'AI Recommendation', 'Value': rec.get('recommendation', 'N/A')}
        rows.append(row)
        row = {'Symbol': symbol, 'Metric': 'AI Action', 'Value': rec.get('action', 'N/A')}
        rows.append(row)
        row = {'Symbol': symbol, 'Metric': 'AI Confidence', 'Value': rec.get('confidence', 'N/A')}
        rows.append(row)

        # Pattern counts
        patterns = analysis_data.get('candlestick_patterns', {})
        bullish = sum(1 for p in patterns.values() if p.get('signal') == 'Bullish')
        bearish = sum(1 for p in patterns.values() if p.get('signal') == 'Bearish')
        row = {'Symbol': symbol, 'Metric': 'Bullish Patterns', 'Value': bullish}
        rows.append(row)
        row = {'Symbol': symbol, 'Metric': 'Bearish Patterns', 'Value': bearish}
        rows.append(row)

        # Contradictions
        contradictions = rec.get('contradictions', [])
        row = {'Symbol': symbol, 'Metric': 'Contradictions', 'Value': len(contradictions)}
        rows.append(row)

        df = pd.DataFrame(rows)
        return df.to_csv(index=False)

    except Exception as e:
        logger.error(f"Error exporting analysis to CSV: {e}")
        return ""


def create_correlation_heatmap(returns_df: pd.DataFrame) -> str:
    """
    Create correlation heatmap from returns DataFrame.

    Args:
        returns_df: DataFrame with returns for each asset

    Returns:
        HTML representation of the heatmap (or empty string if Plotly not available)
    """
    if not PLOTLY_AVAILABLE:
        return ""

    try:
        # Calculate correlation matrix
        corr_matrix = returns_df.corr()

        # Create heatmap
        fig = px.imshow(
            corr_matrix,
            text_auto='.2f',
            aspect='auto',
            color_continuous_scale='RdBu_r',
            zmin=-1, zmax=1,
            title='Asset Correlation Matrix'
        )

        fig.update_layout(
            xaxis_title='Asset',
            yaxis_title='Asset',
            width=600,
            height=600
        )

        return fig.to_html(full_html=False, include_plotlyjs='cdn')

    except Exception as e:
        logger.error(f"Error creating correlation heatmap: {e}")
        return ""


def run_stress_test(portfolio_weights: dict, returns_df: pd.DataFrame,
                    scenarios: list = None) -> dict:
    """
    Run stress tests on a portfolio with various market scenarios.

    Args:
        portfolio_weights: Dict of symbol -> weight
        returns_df: DataFrame with returns for each asset
        scenarios: List of scenario dictionaries (or use defaults)

    Returns:
        Dict with stress test results
    """
    try:
        if scenarios is None:
            scenarios = [
                {'name': 'Market Crash (-20%)', 'market_return': -0.20, 'description': 'Simulated 20% market drop'},
                {'name': 'Moderate Correction (-10%)', 'market_return': -0.10, 'description': 'Simulated 10% market drop'},
                {'name': 'Bull Rally (+15%)', 'market_return': 0.15, 'description': 'Simulated 15% market rise'},
                {'name': 'High Volatility (+30%)', 'market_return': 0.30, 'description': 'Simulated volatile up market'},
                {'name': 'Flash Crash (-30%)', 'market_return': -0.30, 'description': 'Simulated 30% flash crash'},
            ]

        results = {'scenarios': []}

        # Get portfolio return for each scenario
        for scenario in scenarios:
            market_return = scenario['market_return']

            # Assume portfolio beta of ~1.0 (can be calculated from data)
            portfolio_return = market_return * 1.0  # Simplified

            scenario_result = {
                'name': scenario['name'],
                'description': scenario['description'],
                'market_return': f"{market_return:.1%}",
                'portfolio_impact': f"{portfolio_return:.1%}",
                'severity': 'High' if abs(market_return) > 0.2 else ('Medium' if abs(market_return) > 0.1 else 'Low')
            }
            results['scenarios'].append(scenario_result)

        # Calculate worst case
        worst_case = min(s['market_return'] for s in results['scenarios'])
        results['worst_case_scenario'] = 'Flash Crash (-30%)' if worst_case == -0.3 else 'Market Crash (-20%)'
        results['worst_case_impact'] = f"{worst_case:.1%}"

        return results

    except Exception as e:
        logger.error(f"Error running stress test: {e}")
        return {'error': str(e)}


def get_esg_scores(symbol: str, info: dict = None) -> dict:
    """
    Get ESG (Environmental, Social, Governance) scores for a stock.

    Args:
        symbol: Stock symbol
        info: yfinance info dict (optional, will fetch if not provided)

    Returns:
        Dict with ESG information
    """
    try:
        if info is None:
            try:
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                info = ticker.info
            except:
                return {'error': 'Could not fetch ESG data'}

        # Extract ESG-related fields from yfinance info
        esg_data = {
            'symbol': symbol,
            'esg_scores': {},
            'ratings': {}
        }

        # Common ESG field names in yfinance
        esg_fields = {
            'esgScoreOverall': 'Overall ESG',
            'environmentScore': 'Environmental',
            'socialScore': 'Social',
            'governanceScore': 'Governance',
            'esgRating': 'ESG Rating',
            'ratingYear': 'Rating Year',
            'ratingMonth': 'Rating Month',
        }

        for field, label in esg_fields.items():
            if field in info:
                esg_data['esg_scores'][label] = info[field]

        # Carbon metrics
        carbon_fields = {
            'totalEmissions': 'Total Emissions',
            'annualNetEmissions': 'Annual Net Emissions',
            'carbonIntensity': 'Carbon Intensity',
        }

        for field, label in carbon_fields.items():
            if field in info:
                esg_data['carbon'][label] = info[field]

        # Third-party ratings
        rating_fields = {
            'msciRating': 'MSCI Rating',
            'spGlobalRating': 'S&P Global Rating',
        }

        for field, label in rating_fields.items():
            if field in info:
                esg_data['ratings'][label] = info[field]

        # Add mock data for demonstration (real ESG data is often limited)
        if not esg_data['esg_scores']:
            esg_data['esg_scores'] = {
                'Overall ESG': 'Not rated',
                'Environmental': 'Not rated',
                'Social': 'Not rated',
                'Governance': 'Not rated'
            }
            esg_data['note'] = 'ESG ratings not available for this symbol. Consider checking MSCI, Sustainalytics, or Bloomberg for detailed ESG data.'

        return esg_data

    except Exception as e:
        logger.error(f"Error fetching ESG data for {symbol}: {e}")
        return {'error': str(e)}


def analyze_portfolio_risk(portfolio_weights: dict, returns_df: pd.DataFrame) -> dict:
    """
    Comprehensive portfolio risk analysis.

    Args:
        portfolio_weights: Dict of symbol -> weight
        returns_df: DataFrame with returns for each asset

    Returns:
        Dict with risk metrics
    """
    try:
        # Calculate weighted returns
        weights_array = np.array([portfolio_weights.get(sym, 0) for sym in returns_df.columns])
        weights_array = weights_array / weights_array.sum()  # Normalize

        portfolio_returns = (returns_df * weights_array).sum(axis=1)

        # Calculate risk metrics
        volatility = portfolio_returns.std() * np.sqrt(252)
        returns_annual = portfolio_returns.mean() * 252

        # VaR (Value at Risk)
        var_95 = np.percentile(portfolio_returns, 5)
        var_99 = np.percentile(portfolio_returns, 1)

        # Maximum drawdown
        cumulative = (1 + portfolio_returns).cumprod()
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()

        # Skewness and Kurtosis
        skewness = portfolio_returns.skew()
        kurt = portfolio_returns.kurtosis()

        # Concentration risk (Herfindahl-Hirschman Index)
        hhi = (weights_array ** 2).sum()

        return {
            'volatility': volatility,
            'expected_return_annual': returns_annual,
            'var_95_daily': var_95,
            'var_95_annual': var_95 * np.sqrt(252),
            'var_99_daily': var_99,
            'var_99_annual': var_99 * np.sqrt(252),
            'max_drawdown': max_drawdown,
            'skewness': skewness,
            'kurtosis': kurt,
            'concentration_hhi': hhi,
            'concentration_risk': 'High' if hhi > 0.25 else ('Medium' if hhi > 0.15 else 'Low'),
            'num_holdings': len(portfolio_weights),
            'top_holdings': dict(sorted(portfolio_weights.items(), key=lambda x: x[1], reverse=True)[:5])
        }

    except Exception as e:
        logger.error(f"Error analyzing portfolio risk: {e}")
        return {'error': str(e)}
