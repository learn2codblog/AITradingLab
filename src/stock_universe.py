"""
Stock Universe Module for TradeGenius AI
Contains lists of stocks by sector and market cap for Indian markets
"""

# ══════════════════════════════════════════════════════════════════════
# NIFTY 50 STOCKS
# ══════════════════════════════════════════════════════════════════════

NIFTY_50 = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS", "ITC.NS",
    "LT.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "HCLTECH.NS",
    "SUNPHARMA.NS", "TITAN.NS", "BAJFINANCE.NS", "ULTRACEMCO.NS", "WIPRO.NS",
    "NESTLEIND.NS", "TATAMOTORS.NS", "M&M.NS", "NTPC.NS", "POWERGRID.NS",
    "ONGC.NS", "JSWSTEEL.NS", "TATASTEEL.NS", "ADANIENT.NS", "ADANIPORTS.NS",
    "COALINDIA.NS", "GRASIM.NS", "TECHM.NS", "INDUSINDBK.NS", "HINDALCO.NS",
    "DRREDDY.NS", "CIPLA.NS", "BPCL.NS", "EICHERMOT.NS", "BRITANNIA.NS",
    "DIVISLAB.NS", "HEROMOTOCO.NS", "BAJAJ-AUTO.NS", "APOLLOHOSP.NS", "TATACONSUM.NS",
    "UPL.NS", "SBILIFE.NS", "HDFCLIFE.NS", "BAJAJFINSV.NS", "LTIM.NS"
]

# ══════════════════════════════════════════════════════════════════════
# SECTOR-WISE STOCK LISTS
# ══════════════════════════════════════════════════════════════════════

BANKING_STOCKS = [
    "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS",
    "INDUSINDBK.NS", "BANKBARODA.NS", "PNB.NS", "CANBK.NS", "UNIONBANK.NS",
    "IDFCFIRSTB.NS", "BANDHANBNK.NS", "FEDERALBNK.NS", "RBLBANK.NS", "AUBANK.NS",
    "IDBI.NS", "MAHABANK.NS", "IOB.NS", "CENTRALBK.NS", "UCOBANK.NS",
    "J&KBANK.NS", "CUB.NS"
]

IT_STOCKS = [
    "TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS",
    "LTIM.NS", "MPHASIS.NS", "COFORGE.NS", "PERSISTENT.NS", "LTTS.NS",
    "MINDTREE.NS", "NIITTECH.NS", "TATAELXSI.NS", "HAPPSTMNDS.NS", "ROUTE.NS",
    "SONATSOFTW.NS", "CYIENT.NS", "ZENTEC.NS"
]

PHARMA_STOCKS = [
    "SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS", "APOLLOHOSP.NS",
    "BIOCON.NS", "LUPIN.NS", "AUROPHARMA.NS", "TORNTPHARM.NS", "ALKEM.NS",
    "ABBOTINDIA.NS", "GLAXO.NS", "PFIZER.NS", "SANOFI.NS", "IPCALAB.NS",
    "LAURUSLABS.NS", "NATCOPHARM.NS", "GLENMARK.NS", "CADILAHC.NS", "GRANULES.NS",
    "AJANTPHARM.NS", "APLLTD.NS", "JUBILANT.NS", "SYNGENE.NS"
]

AUTO_STOCKS = [
    "MARUTI.NS", "TATAMOTORS.NS", "M&M.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS",
    "HEROMOTOCO.NS", "ASHOKLEY.NS", "TVSMOTOR.NS", "BHARATFORG.NS", "BOSCHLTD.NS",
    "MRF.NS", "BALKRISIND.NS", "APOLLOTYRE.NS", "MOTHERSUMI.NS", "EXIDEIND.NS",
    "AMARAJABAT.NS", "CEATLTD.NS", "ENDURANCE.NS", "SUNDRMFAST.NS", "FORCEMOT.NS",
    "ESCORTS.NS", "SWARAJENG.NS", "TIINDIA.NS"
]

ENERGY_STOCKS = [
    "RELIANCE.NS", "ONGC.NS", "NTPC.NS", "POWERGRID.NS", "BPCL.NS",
    "COALINDIA.NS", "IOC.NS", "GAIL.NS", "PETRONET.NS", "HINDPETRO.NS",
    "ADANIGREEN.NS", "TATAPOWER.NS", "NHPC.NS", "TORNTPOWER.NS", "CESC.NS",
    "ADANIPOWER.NS", "RPOWER.NS", "SJVN.NS", "NLCINDIA.NS", "IREDA.NS",
    "PTC.NS"
]

FMCG_STOCKS = [
    "HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "BRITANNIA.NS", "TATACONSUM.NS",
    "DABUR.NS", "MARICO.NS", "GODREJCP.NS", "COLPAL.NS", "PGHH.NS",
    "EMAMILTD.NS", "RADICO.NS", "VBL.NS", "MCDOWELL-N.NS", "TATACONSUM.NS",
    "VENKEYS.NS", "BIKAJI.NS", "VARUNBEV.NS"
]

METALS_STOCKS = [
    "TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS", "COALINDIA.NS",
    "NMDC.NS", "SAIL.NS", "JINDALSTEL.NS", "NATIONALUM.NS", "MOIL.NS",
    "HINDZINC.NS", "APLAPOLLO.NS", "RATNAMANI.NS", "WELCORP.NS", "GPPL.NS"
]

# Cement Sector - Dedicated sector for cement stocks
CEMENT_STOCKS = [
    "ULTRACEMCO.NS", "SHREECEM.NS", "AMBUJACEM.NS", "ACC.NS", "DALBHARAT.NS",
    "RAMCOCEM.NS", "JKCEMENT.NS", "JKLAKSHMI.NS", "BIRLACEM.NS", "PRSMJOHNSN.NS",
    "HEIDELBERG.NS", "INDIACEM.NS", "ORIENTCEM.NS", "SAGCEM.NS", "STARCEMENT.NS",
    "SAGAR.NS", "KESORAMIND.NS", "NCLIND.NS", "DECCANCEM.NS", "BURNPUR.NS"
]

INFRASTRUCTURE_STOCKS = [
    "LT.NS", "ADANIENT.NS", "ADANIPORTS.NS", "GRASIM.NS",
    "GMRINFRA.NS", "IRB.NS", "NBCC.NS", "HCC.NS", "NCC.NS",
    "ENGINERSIN.NS", "BEL.NS", "HAL.NS", "BEML.NS", "COCHINSHIP.NS",
    "GRSE.NS", "MDL.NS", "PFC.NS", "RECLTD.NS", "IRFC.NS", "RVNL.NS",
    "KEC.NS", "KALPATPOWR.NS", "CUMMINSIND.NS", "SIEMENS.NS", "ABB.NS"
]

FINANCIAL_SERVICES = [
    "BAJFINANCE.NS", "BAJAJFINSV.NS", "SBILIFE.NS", "HDFCLIFE.NS", "ICICIPRULI.NS",
    "ICICIGI.NS", "SBICARD.NS", "CHOLAFIN.NS", "M&MFIN.NS", "LICHSGFIN.NS",
    "SHRIRAMFIN.NS", "MANAPPURAM.NS", "MUTHOOTFIN.NS", "POONAWALLA.NS", "CREDITACC.NS",
    "AAVAS.NS", "CANFINHOME.NS", "HOMEFIRST.NS", "ANGELONE.NS", "MOTILALOFS.NS"
]

CONSUMER_DURABLES = [
    "TITAN.NS", "HAVELLS.NS", "VOLTAS.NS", "BLUESTARCO.NS", "WHIRLPOOL.NS",
    "CROMPTON.NS", "VGUARD.NS", "AMBER.NS", "DIXON.NS", "KAJARIACER.NS",
    "CERA.NS", "BATAINDIA.NS", "RELAXO.NS", "PAGEIND.NS", "RAJESHEXPO.NS"
]

REALTY_STOCKS = [
    "DLF.NS", "GODREJPROP.NS", "OBEROIRLTY.NS", "PRESTIGE.NS", "PHOENIXLTD.NS",
    "BRIGADE.NS", "SOBHA.NS", "SUNTECK.NS", "MAHLIFE.NS", "LODHA.NS",
    "RUSTOMJEE.NS"
]

TELECOM_STOCKS = [
    "BHARTIARTL.NS", "IDEA.NS", "TATACOMM.NS", "INDIAMART.NS", "ROUTE.NS",
    "STLTECH.NS", "HFCL.NS", "TEJAS.NS", "GTPL.NS"
]

MEDIA_ENTERTAINMENT = [
    "ZEEL.NS", "SUNTV.NS", "NETWORK18.NS", "TV18BRDCST.NS", "PVR.NS",
    "INOXLEISUR.NS", "NAZARA.NS", "RADIOCITY.NS", "TIPSINDLTD.NS", "SAREGAMA.NS"
]

# ══════════════════════════════════════════════════════════════════════
# MARKET CAP BASED LISTS
# ══════════════════════════════════════════════════════════════════════

LARGE_CAP = NIFTY_50 + [
    "ADANIGREEN.NS", "ADANITRANS.NS", "PIDILITIND.NS", "SIEMENS.NS", "ABB.NS",
    "HAVELLS.NS", "VEDL.NS", "BANKBARODA.NS", "GODREJPROP.NS", "DLF.NS",
    "IOC.NS", "GAIL.NS", "TRENT.NS", "ZOMATO.NS", "PAYTM.NS"
]

MID_CAP = [
    "MPHASIS.NS", "COFORGE.NS", "PERSISTENT.NS", "TATAELXSI.NS", "LTTS.NS",
    "AUBANK.NS", "BANDHANBNK.NS", "FEDERALBNK.NS", "CROMPTON.NS", "VOLTAS.NS",
    "CUMMINSIND.NS", "TRENT.NS", "JUBLFOOD.NS", "PAGEIND.NS", "MCDOWELL-N.NS",
    "POLYCAB.NS", "ASTRAL.NS", "SUPREMEIND.NS", "AFFLE.NS", "HAPPSTMNDS.NS",
    "ZYDUSLIFE.NS", "LAURUSLABS.NS", "TORNTPHARM.NS", "IPCALAB.NS", "GLAXO.NS",
    "ABBOTINDIA.NS", "ALKEM.NS", "METROPOLIS.NS", "LALPATHLAB.NS", "MAXHEALTH.NS"
]

SMALL_CAP = [
    "CDSL.NS", "KPITTECH.NS", "BIRLASOFT.NS", "TANLA.NS", "MASTEK.NS",
    "GTPL.NS", "LXCHEM.NS", "FINEORG.NS", "CLEAN.NS", "ALKYLAMINE.NS",
    "DEEPAKFERT.NS", "AARTIIND.NS", "TATAINVEST.NS", "GILLETTE.NS", "3MINDIA.NS",
    "HONAUT.NS", "SCHAEFFLER.NS", "SKFINDIA.NS", "TIMKEN.NS", "GRINDWELL.NS",
    "CARBORUNIV.NS", "CERA.NS", "ORIENTELEC.NS", "BALAMINES.NS", "GALAXYSURF.NS"
]

# ══════════════════════════════════════════════════════════════════════
# SECTOR MAPPING
# ══════════════════════════════════════════════════════════════════════

SECTOR_STOCKS = {
    "Banking": BANKING_STOCKS,
    "IT": IT_STOCKS,
    "Pharma & Healthcare": PHARMA_STOCKS,
    "Automobile": AUTO_STOCKS,
    "Energy & Power": ENERGY_STOCKS,
    "FMCG": FMCG_STOCKS,
    "Metals & Mining": METALS_STOCKS,
    "Cement": CEMENT_STOCKS,
    "Infrastructure & Construction": INFRASTRUCTURE_STOCKS,
    "Financial Services": FINANCIAL_SERVICES,
    "Consumer Durables": CONSUMER_DURABLES,
    "Realty": REALTY_STOCKS,
    "Telecom": TELECOM_STOCKS,
    "Media & Entertainment": MEDIA_ENTERTAINMENT
}

# ══════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════

def get_all_stocks():
    """Get all unique stocks from all sectors"""
    all_stocks = set()
    for sector_stocks in SECTOR_STOCKS.values():
        all_stocks.update(sector_stocks)
    all_stocks.update(LARGE_CAP)
    all_stocks.update(MID_CAP)
    all_stocks.update(SMALL_CAP)
    return list(all_stocks)


def get_stocks_by_sector(sector: str, limit: int = None):
    """Get stocks for a specific sector"""
    stocks = SECTOR_STOCKS.get(sector, [])
    if limit:
        return stocks[:limit]
    return stocks


def get_all_sectors():
    """Get list of all available sectors"""
    return list(SECTOR_STOCKS.keys())


def get_indian_stocks_by_sector():
    """
    Get all Indian stocks organized by sector

    Returns:
        Dict mapping sector names to lists of stock symbols
    """
    return SECTOR_STOCKS.copy()


def get_stocks_by_market_cap(cap_type: str, limit: int = None):
    """
    Get stocks by market cap category

    Args:
        cap_type: 'large', 'mid', or 'small'
        limit: Maximum number of stocks

    Returns:
        List of stock symbols
    """
    if cap_type.lower() == 'large':
        stocks = LARGE_CAP
    elif cap_type.lower() == 'mid':
        stocks = MID_CAP
    elif cap_type.lower() == 'small':
        stocks = SMALL_CAP
    else:
        stocks = NIFTY_50

    if limit:
        return stocks[:limit]
    return stocks


def get_nifty_50():
    """Get Nifty 50 stocks"""
    return NIFTY_50.copy()


def search_stock(query: str):
    """
    Search for stocks matching query

    Args:
        query: Search string

    Returns:
        List of matching stock symbols
    """
    query = query.upper()
    all_stocks = get_all_stocks()

    matches = [s for s in all_stocks if query in s.upper()]
    return matches


def get_stock_universe_by_sector(sector: str, limit: int = 100) -> list:
    """
    Get stocks for a specific sector from comprehensive universe

    Args:
        sector: Sector name (case-insensitive match)
        limit: Maximum number of stocks to return

    Returns:
        List of stock symbols for the sector
    """
    # Try exact match first
    if sector in SECTOR_STOCKS:
        stocks = SECTOR_STOCKS[sector]
        return stocks[:limit] if limit else stocks

    # Try case-insensitive partial match
    sector_lower = sector.lower()
    for sector_name, stocks in SECTOR_STOCKS.items():
        if sector_lower in sector_name.lower() or sector_name.lower() in sector_lower:
            return stocks[:limit] if limit else stocks

    # Map common sector aliases
    sector_aliases = {
        'bank': 'Banking',
        'banks': 'Banking',
        'tech': 'IT',
        'technology': 'IT',
        'information technology': 'IT',
        'software': 'IT',
        'pharma': 'Pharma & Healthcare',
        'healthcare': 'Pharma & Healthcare',
        'pharmaceutical': 'Pharma & Healthcare',
        'auto': 'Automobile',
        'automotive': 'Automobile',
        'vehicles': 'Automobile',
        'energy': 'Energy & Power',
        'power': 'Energy & Power',
        'oil': 'Energy & Power',
        'oil & gas': 'Energy & Power',
        'consumer goods': 'FMCG',
        'fmcg': 'FMCG',
        'metals': 'Metals & Mining',
        'mining': 'Metals & Mining',
        'steel': 'Metals & Mining',
        'cement': 'Cement',
        'construction': 'Infrastructure & Construction',
        'infra': 'Infrastructure & Construction',
        'infrastructure': 'Infrastructure & Construction',
        'finance': 'Financial Services',
        'nbfc': 'Financial Services',
        'insurance': 'Financial Services',
        'consumer': 'Consumer Durables',
        'durables': 'Consumer Durables',
        'real estate': 'Realty',
        'realty': 'Realty',
        'property': 'Realty',
        'telecom': 'Telecom',
        'telecommunications': 'Telecom',
        'media': 'Media & Entertainment',
        'entertainment': 'Media & Entertainment'
    }

    mapped_sector = sector_aliases.get(sector_lower)
    if mapped_sector and mapped_sector in SECTOR_STOCKS:
        stocks = SECTOR_STOCKS[mapped_sector]
        return stocks[:limit] if limit else stocks

    # Return empty list if sector not found
    return []


def load_custom_universe_by_sector(csv_path: str = None) -> dict:
    """
    Load custom stock universe from a CSV file

    Args:
        csv_path: Path to CSV file with 'Symbol' and 'Sector' columns

    Returns:
        Dict mapping sector names to lists of stock symbols
    """
    import os
    import pandas as pd

    # Default paths to search
    if csv_path is None:
        possible_paths = [
            "stock_universe.csv",
            "data/stock_universe.csv",
            "universe.csv",
            "data/universe.csv",
            "nifty_top_400.csv",
            "data/nifty_top_400.csv"
        ]
    else:
        possible_paths = [csv_path]

    for path in possible_paths:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)

                # Check for required columns
                if 'Symbol' in df.columns and 'Sector' in df.columns:
                    # Group by sector
                    sector_dict = {}
                    for sector in df['Sector'].unique():
                        sector_stocks = df[df['Sector'] == sector]['Symbol'].tolist()
                        # Add .NS suffix if not present
                        sector_stocks = [s if s.endswith('.NS') else f"{s}.NS" for s in sector_stocks]
                        sector_dict[sector] = sector_stocks
                    return sector_dict

                elif 'Symbol' in df.columns:
                    # If only Symbol column, return all under 'All' sector
                    symbols = df['Symbol'].tolist()
                    symbols = [s if s.endswith('.NS') else f"{s}.NS" for s in symbols]
                    return {'All': symbols}

            except Exception as e:
                print(f"Error loading {path}: {e}")
                continue

    # Return built-in sectors if no custom file found
    return SECTOR_STOCKS.copy()


def get_comprehensive_sector_list() -> list:
    """
    Get comprehensive list of all available sectors

    Returns:
        List of sector names with stock counts
    """
    sectors_with_counts = []
    for sector, stocks in SECTOR_STOCKS.items():
        sectors_with_counts.append(f"{sector} ({len(stocks)} stocks)")
    return sectors_with_counts

