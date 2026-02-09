"""
Enhanced stock database with sector-wise classification for broader universe
"""

import os
import pandas as pd


def get_indian_stocks_by_sector() -> dict:
    """
    Get Indian stocks organized by sector from a larger universe (Nifty 500 level)

    Returns:
        Dict mapping sector names to list of stocks
    """
    stocks_by_sector = {
        'Banking': [
            # Public Sector Banks
            'SBIN.NS', 'PNB.NS', 'BANKBARODA.NS', 'BANKINDIA.NS', 'CANBK.NS',
            'UNIONBANK.NS', 'INDIANB.NS', 'CENTRALBK.NS', 'IDFCFIRSTB.NS',
            # Private Banks
            'HDFCBANK.NS', 'ICICIBANK.NS', 'AXISBANK.NS', 'KOTAKBANK.NS',
            'INDUSINDBK.NS', 'FEDERALBNK.NS', 'BANDHANBNK.NS', 'RBLBANK.NS',
            'YESBANK.NS', 'AUBANK.NS', 'DCBBANK.NS', 'SOUTHBANK.NS'
        ],

        'IT': [
            # Large Cap IT
            'TCS.NS', 'INFY.NS', 'WIPRO.NS', 'HCLTECH.NS', 'TECHM.NS', 'LTIM.NS',
            # Mid Cap IT
            'COFORGE.NS', 'PERSISTENT.NS', 'MPHASIS.NS', 'LTTS.NS',
            'MINDTREE.NS', 'CYIENT.NS', 'ZENSAR.NS', 'HEXAWARE.NS',
            'NIITTECH.NS', 'SONATSOFTW.NS', 'KPIT.NS', 'TATAELXSI.NS'
        ],

        'Energy': [
            # Oil & Gas
            'RELIANCE.NS', 'ONGC.NS', 'BPCL.NS', 'IOC.NS', 'GAIL.NS',
            'OIL.NS', 'HINDPETRO.NS', 'MGL.NS', 'IGL.NS', 'PETRONET.NS',
            # Power
            'NTPC.NS', 'POWERGRID.NS', 'ADANIGREEN.NS', 'TATAPOWER.NS',
            'ADANIPOWER.NS', 'TORNTPOWER.NS', 'NHPC.NS', 'SJVN.NS',
            'CESC.NS', 'JSWENERGY.NS', 'JPPOWER.NS'
        ],

        'Pharma': [
            # Large Pharma
            'SUNPHARMA.NS', 'DRREDDY.NS', 'CIPLA.NS', 'DIVISLAB.NS', 'AUROPHARMA.NS',
            # Mid Pharma
            'LUPIN.NS', 'BIOCON.NS', 'TORNTPHARM.NS', 'ALKEM.NS', 'ABBOTINDIA.NS',
            'GLAXO.NS', 'PFIZER.NS', 'SANOFI.NS', 'ASTRAZEN.NS', 'ZYDUSLIFE.NS',
            'CADILAHC.NS', 'IPCALAB.NS', 'LAURUSLABS.NS', 'LALPATHLAB.NS',
            'METROPOLIS.NS', 'APOLLOHOSP.NS', 'FORTIS.NS', 'MAXHEALTH.NS'
        ],

        'Auto': [
            # Auto Manufacturers
            'MARUTI.NS', 'TATAMOTORS.NS', 'M&M.NS', 'EICHERMOT.NS', 'HEROMOTOCORP.NS',
            'BAJAJ-AUTO.NS', 'TVS.NS', 'ASHOKLEY.NS', 'ESCORTS.NS', 'FORCEMOT.NS',
            # Auto Components
            'BOSCHLTD.NS', 'MOTHERSON.NS', 'BALKRISIND.NS', 'MRF.NS', 'APOLLOTYRE.NS',
            'EXIDEIND.NS', 'AMBUJACEM.NS', 'CEATLTD.NS', 'ENDURANCE.NS', 'SUPRAJIT.NS',
            'SONA.NS', 'SUNDRMFAST.NS', 'BHARAT.NS'
        ],

        'Metals': [
            # Steel
            'TATASTEEL.NS', 'JSWSTEEL.NS', 'SAIL.NS', 'JINDALSTEL.NS', 'NMDC.NS',
            'VEDL.NS', 'HINDALCO.NS', 'NATIONALUM.NS', 'HINDZINC.NS',
            # Non-Ferrous
            'HINDCOPPER.NS', 'RATNAMANI.NS', 'WELCORP.NS', 'WELSPUNIND.NS',
            'JSPL.NS', 'GODREJCP.NS'
        ],

        'Cement': [
            'ULTRACEMCO.NS', 'AMBUJACEM.NS', 'ACC.NS', 'SHREECEM.NS', 'DALMIACEM.NS',
            'JKCEMENT.NS', 'RAMCOCEM.NS', 'INDIACEM.NS', 'HEIDELBERG.NS', 'BIRLACEM.NS'
        ],

        'FMCG': [
            # Foods & Beverages
            'NESTLEIND.NS', 'BRITANNIA.NS', 'DABUR.NS', 'MARICO.NS', 'GODREJCP.NS',
            'VBL.NS', 'TATACONSUM.NS', 'ITC.NS', 'HINDUNILVR.NS', 'COLPAL.NS',
            # Personal Care
            'PGHH.NS', 'EMAMILTD.NS', 'GILLETTE.NS', 'JYOTHYLAB.NS', 'BAJAJHIND.NS',
            'RADICO.NS', 'MCDOWELL-N.NS', 'VARUN.NS', 'CCL.NS'
        ],

        'Infra': [
            'LT.NS', 'ADANIPORTS.NS', 'ADANIENT.NS', 'GUJGASLTD.NS',
            'IRB.NS', 'NBCC.NS', 'JKPAPER.NS', 'NCC.NS', 'LTTS.NS', 'KEC.NS',
            'THERMAX.NS', 'ABB.NS', 'SIEMENS.NS', 'HAVELLS.NS', 'VOLTAS.NS',
            'CROMPTON.NS', 'CUMMINSIND.NS', 'BEML.NS', 'BEL.NS', 'HAL.NS'
        ],

        'Telecom': [
            'BHARTIARTL.NS', 'INDUSINDBK.NS', 'TATACOMM.NS', 'GTPL.NS',
            'ROUTE.NS', 'ONMOBILE.NS'
        ],

        'Financials': [
            # NBFCs
            'BAJAJFINSV.NS', 'BAJFINANCE.NS', 'M&MFIN.NS', 'CHOLAFIN.NS',
            'SHRIRAMFIN.NS', 'LICHSGFIN.NS', 'PFC.NS', 'RECLTD.NS',
            'MUTHOOTFIN.NS', 'MANAPPURAM.NS', 'IIFL.NS', 'PEL.NS',
            # Insurance
            'SBILIFE.NS', 'HDFCLIFE.NS', 'ICICIPRULI.NS', 'ICICIGI.NS',
            'SBICARD.NS', 'HDFCAMC.NS', 'NIACL.NS'
        ],

        'Consumer': [
            # Retail & Consumer Durables
            'ASIANPAINT.NS', 'TITAN.NS', 'PIDILITIND.NS', 'BERGEPAINT.NS',
            'AFFLE.NS', 'INDIGO.NS', 'SPICEJET.NS', 'PVRINOX.NS', 'INOXLEISUR.NS',
            # Electronics
            'DIXON.NS', 'AMBER.NS', 'KAJARIACER.NS', 'BLUESTARCO.NS',
            'SYMPHONY.NS', 'RAJESHEXPO.NS', 'JUBLFOOD.NS', 'WESTLIFE.NS',
            'DEVYANI.NS', 'SAPPHIRE.NS', 'PNBHOUSING.NS'
        ],

        'Media': [
            'ZEEL.NS', 'SUNTV.NS', 'NETWORK18.NS', 'TVTODAY.NS', 'NAZARA.NS',
            'SAREGAMA.NS', 'TIPS.NS', 'PVR.NS', 'INOXLEISUR.NS'
        ],

        'Textiles': [
            'GRASIM.NS', 'AIAENG.NS', 'RAYMOND.NS', 'SPTL.NS', 'ARVIND.NS',
            'VARDHACRLC.NS', 'WELSPUNIND.NS', 'RUPA.NS', 'CANTABIL.NS',
            'SPANDANA.NS', 'GARFIBRES.NS'
        ],

        'Chemicals': [
            'UPL.NS', 'SRF.NS', 'AARTI.NS', 'DEEPAKNI.NS', 'TATACHEM.NS',
            'GNFC.NS', 'GUJALKALI.NS', 'FINEORG.NS', 'NAVINFLUOR.NS',
            'PI.NS', 'ALKYLAMINE.NS', 'BALAJI.NS', 'ATUL.NS', 'CHAMBLFERT.NS'
        ],

        'Real Estate': [
            'DLF.NS', 'GODREJPROP.NS', 'BRIGADE.NS', 'PRESTIGE.NS', 'OBEROIRLTY.NS',
            'PHOENIXLTD.NS', 'SOBHA.NS', 'IBREALEST.NS', 'SUNTECK.NS', 'MAHLIFE.NS'
        ]
    }

    return stocks_by_sector


def get_stock_universe_by_sector(sector: str, universe_size: int = 400) -> list:
    """
    Get stocks for a specific sector, with fallback to larger universe

    Args:
        sector: Sector name
        universe_size: Maximum number of stocks to return

    Returns:
        List of stock symbols for the sector
    """
    stocks_by_sector = get_indian_stocks_by_sector()

    # Get stocks for the specified sector
    if sector in stocks_by_sector:
        sector_stocks = stocks_by_sector[sector]
        return sector_stocks[:universe_size]

    return []


def get_all_sectors() -> list:
    """
    Get list of all available sectors

    Returns:
        List of sector names
    """
    return list(get_indian_stocks_by_sector().keys())


def load_custom_universe_by_sector(csv_path: str = None) -> dict:
    """
    Load sector-wise stocks from a custom CSV file

    CSV Format Expected:
    Symbol,Sector
    RELIANCE.NS,Energy
    TCS.NS,IT
    ...

    Args:
        csv_path: Path to CSV file (optional)

    Returns:
        Dict mapping sectors to list of stocks
    """
    # Try to find CSV file
    if csv_path is None:
        candidates = [
            "stock_universe.csv",
            "nifty_500.csv",
            "data/stock_universe.csv",
            "data/nifty_500.csv"
        ]
        for path in candidates:
            if os.path.exists(path):
                csv_path = path
                break

    if csv_path and os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)

            # Check if both Symbol and Sector columns exist
            if 'Symbol' in df.columns and 'Sector' in df.columns:
                # Group by sector
                sector_dict = {}
                for sector in df['Sector'].unique():
                    if pd.notna(sector):
                        sector_stocks = df[df['Sector'] == sector]['Symbol'].tolist()
                        sector_dict[sector] = sector_stocks

                return sector_dict
        except Exception as e:
            print(f"Error loading custom universe: {e}")

    # Fallback to built-in data
    return get_indian_stocks_by_sector()

