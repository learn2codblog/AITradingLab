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

INFRASTRUCTURE_STOCKS = [
    "LT.NS", "ADANIENT.NS", "ADANIPORTS.NS", "ULTRACEMCO.NS", "GRASIM.NS",
    "SHREECEM.NS", "AMBUJACEM.NS", "ACC.NS", "DALBHARAT.NS", "RAMCOCEM.NS",
    "GMRINFRA.NS", "IRB.NS", "NBCC.NS", "HCC.NS", "NCC.NS",
    "ENGINERSIN.NS", "BEL.NS", "HAL.NS", "BEML.NS", "COCHINSHIP.NS",
    "GRSE.NS", "MDL.NS"
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

