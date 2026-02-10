"""
Modern UI Styles and Theme Configuration
"""

def get_custom_css():
    """Return custom CSS for modern UI styling"""
    return """
    <style>
        /* ══════════════════════════════════════════════════════════════ */
        /* LAYOUT & GENERAL */
        /* ══════════════════════════════════════════════════════════════ */
        
        /* Hide Sidebar Completely */
        [data-testid="stSidebar"] {
            display: none;
        }

        /* Adjust main content to use full width */
        .main .block-container {
            max-width: 100%;
            padding-left: 2rem;
            padding-right: 2rem;
        }

        /* Main App Styling with Modern Background */
        .main {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 1rem;
        }
        
        body {
            color: #111;
        }

        /* Top Navigation Buttons */
        .stButton > button {
            width: 100%;
            background: rgba(255, 255, 255, 0.15);
            color: #111;
            border: none;
            font-weight: 600;
            padding: 0.75rem 1rem;
            border-radius: 30px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            backdrop-filter: blur(10px);
        }

        .stButton > button:hover {
            background: rgba(255, 255, 255, 0.25);
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
        }

        .stButton > button:active {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            box-shadow: 0 8px 25px rgba(245, 87, 108, 0.4);
            transform: scale(1.05);
        }

        /* Primary Button Override */
        button[kind="primary"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.75rem 1.5rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }

        button[kind="primary"]:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4) !important;
        }

        /* Card Styling */
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }

        /* Custom Card */
        .custom-card {
            background: white;
            border-radius: 16px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.08);
            margin: 15px 0;
            border: 1px solid rgba(102, 126, 234, 0.1);
            transition: all 0.3s ease;
        }
        
        .custom-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 40px rgba(102, 126, 234, 0.15);
        }

        /* Metric Cards */
        div[data-testid="stMetricValue"] {
            font-size: 2.2rem;
            font-weight: 800;
            color: #2d3748;
        }

        div[data-testid="metric-container"] {
            background: linear-gradient(135deg, white 0%, rgba(240, 147, 251, 0.05) 100%);
            padding: 20px;
            border-radius: 16px;
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.08);
            border: 1px solid rgba(102, 126, 234, 0.1);
            transition: all 0.3s ease;
        }
        
        div[data-testid="metric-container"]:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 30px rgba(102, 126, 234, 0.15);
        }

        /* Headers with modern gradient */
        h1 {
            color: #2d3748;
            font-weight: 900;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            padding: 0.5rem 0;
            font-size: 2.5rem;
        }

        h2, h3 {
            color: #2d3748;
            font-weight: 800;
        }
        
        h2 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        /* Input fields styling */
        input, select, textarea {
            border-radius: 12px !important;
            border: 2px solid rgba(102, 126, 234, 0.2) !important;
            transition: all 0.3s ease !important;
        }

        input:focus, select:focus, textarea:focus {
            border-color: #667eea !important;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
        }

        /* Expander styling */
        .streamlit-expanderHeader {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(240, 147, 251, 0.05) 100%);
            border: 1px solid rgba(102, 126, 234, 0.2);
            border-radius: 12px;
            transition: all 0.3s ease;
        }

        .streamlit-expanderHeader:hover {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(240, 147, 251, 0.1) 100%);
        }

        /* Dataframe styling */
        .dataframe {
            border-collapse: collapse !important;
            border-radius: 12px !important;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        table {
            background: white;
            border-radius: 12px;
            overflow: hidden;
        }

        table thead {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        table tbody tr {
            border-bottom: 1px solid rgba(102, 126, 234, 0.1);
            transition: all 0.3s ease;
        }

        table tbody tr:hover {
            background: rgba(102, 126, 234, 0.05);
        }

        /* Success & Info messages */
        .stSuccess {
            background: linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(102, 255, 102, 0.05) 100%) !important;
            border-left: 4px solid #4CAF50 !important;
            border-radius: 12px !important;
            padding: 15px !important;
        }

        .stInfo {
            background: linear-gradient(135deg, rgba(33, 150, 243, 0.1) 0%, rgba(102, 204, 255, 0.05) 100%) !important;
            border-left: 4px solid #2196F3 !important;
            border-radius: 12px !important;
            padding: 15px !important;
        }

        .stWarning {
            background: linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 179, 102, 0.05) 100%) !important;
            border-left: 4px solid #ff9800 !important;
            border-radius: 12px !important;
            padding: 15px !important;
        }

        .stError {
            background: linear-gradient(135deg, rgba(244, 67, 54, 0.1) 0%, rgba(255, 102, 102, 0.05) 100%) !important;
            border-left: 4px solid #f44336 !important;
            border-radius: 12px !important;
            padding: 15px !important;
        }

        /* Slider styling */
        .stSlider > div {
            border-radius: 12px;
        }

        /* Checkbox styling */
        .stCheckbox {
            color: #2d3748;
        }

        /* ══════════════════════════════════════════════════════════════ */
        /* HEADER STYLES */
        /* ══════════════════════════════════════════════════════════════ */
        
        .header-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            padding: 40px 45px;
            border-radius: 24px;
            margin-bottom: 20px;
            box-shadow: 0 15px 40px rgba(102, 126, 234, 0.3), inset 0 1px 1px rgba(255, 255, 255, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.25);
            backdrop-filter: blur(20px);
            position: relative;
            overflow: hidden;
            z-index: 10001;
            pointer-events: auto;
        }
        
        .header-box::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -10%;
            width: 300px;
            height: 300px;
            background: radial-gradient(circle, rgba(245, 87, 108, 0.2) 0%, transparent 70%);
            border-radius: 50%;
            pointer-events: none;
        }
        
        .header-box::after {
            content: '';
            position: absolute;
            bottom: -30%;
            left: -5%;
            width: 250px;
            height: 250px;
            background: radial-gradient(circle, rgba(240, 147, 251, 0.15) 0%, transparent 70%);
            border-radius: 50%;
            pointer-events: none;
        }
        
        .app-title {
            color: #ffffff;
            font-size: 3.2rem;
            font-weight: 900;
            margin: 0;
            padding: 0;
            text-shadow: 3px 3px 12px rgba(0, 0, 0, 0.35);
            letter-spacing: -1px;
            position: relative;
            z-index: 1;
        }
        
        .app-tagline {
            color: #ffffff;
            font-size: 1.15rem;
            font-weight: 600;
            margin: 12px 0 0 0;
            background: rgba(255, 255, 255, 0.15);
            padding: 10px 20px;
            border-radius: 30px;
            display: inline-block;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.25);
            position: relative;
            z-index: 1;
        }
        
        .version-badge {
            background: linear-gradient(135deg, rgba(245, 87, 108, 0.9) 0%, rgba(240, 147, 251, 0.9) 100%);
            padding: 12px 26px;
            border-radius: 30px;
            color: #ffffff;
            font-weight: 700;
            font-size: 0.95rem;
            border: 1px solid rgba(255, 255, 255, 0.3);
            display: inline-block;
            text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
            box-shadow: 0 6px 20px rgba(245, 87, 108, 0.25);
            position: relative;
            z-index: 1;
        }
        
        .user-info {
            text-align: right;
            padding-top: 8px;
            position: relative;
            z-index: 10002;
            pointer-events: auto;
        }
        
        .user-name {
            color: #ffffff;
            font-weight: 700;
            font-size: 0.95rem;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
            margin: 0;
        }
        
        .user-email {
            color: rgba(255, 255, 255, 0.85);
            font-size: 0.85rem;
            margin-top: 2px;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
        }

        /* ══════════════════════════════════════════════════════════════ */
        /* NAVIGATION STYLES */
        /* ══════════════════════════════════════════════════════════════ */
        
        .nav-container {
            display: flex;
            gap: 8px;
            padding: 12px 20px;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.95) 0%, rgba(118, 75, 162, 0.95) 100%);
            border-radius: 50px;
            margin-bottom: 25px;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            flex-wrap: wrap;
            justify-content: center;
            border: 1px solid rgba(255, 255, 255, 0.15);
            position: relative;
            z-index: 100;
        }
        
        .nav-btn {
            padding: 10px 18px !important;
            border-radius: 30px !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            border: none !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            background: rgba(255, 255, 255, 0.15) !important;
            color: white !important;
            white-space: nowrap;
            cursor: pointer;
            position: relative;
            overflow: hidden;
            pointer-events: auto !important;
            z-index: 101;
        }
        
        .nav-btn:hover {
            background: rgba(255, 255, 255, 0.25) !important;
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15) !important;
        }
        
        .nav-btn.active {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
            box-shadow: 0 8px 25px rgba(245, 87, 108, 0.3) !important;
            transform: scale(1.05);
        }

        /* ══════════════════════════════════════════════════════════════ */
        /* RESPONSIVE & MOBILE DESIGN */
        /* ══════════════════════════════════════════════════════════════ */
        
        @media (max-width: 768px) {
            .nav-container {
                gap: 6px;
                padding: 10px 12px;
                justify-content: flex-start;
                overflow-x: auto;
            }
            .nav-btn {
                padding: 8px 14px !important;
                font-size: 0.85rem !important;
            }
            
            /* Navigation buttons stack vertically on mobile */
            [data-testid="column"] {
                flex-wrap: wrap;
            }
            
            /* Reduce padding and margins on mobile */
            .stMetric {
                padding: 0.5rem;
            }
            
            /* Make selectbox full width on mobile */
            .stSelectbox {
                width: 100%;
            }
            
            /* Stack columns on mobile */
            .stColumn {
                width: 100% !important;
                margin-bottom: 1rem;
            }
            
            /* Responsive font sizes */
            h1 { font-size: 1.5rem; }
            h2 { font-size: 1.2rem; }
            h3 { font-size: 1rem; }
            
            /* Full width buttons on mobile */
            .stButton button {
                width: 100%;
            }
            
            /* Reduce chart height on mobile */
            .plotly-graph-div {
                height: 250px !important;
            }
        }
        
        @media (max-width: 480px) {
            /* Extra small devices */
            .header-box {
                padding: 20px;
            }
            
            .app-title {
                font-size: 1.8rem;
            }
            
            .app-tagline {
                font-size: 0.9rem;
            }
            
            /* Single column layout on very small screens */
            [data-testid="column"] {
                width: 100% !important;
            }
        }
        
        /* General responsive improvements */
        .stDataFrame {
            overflow-x: auto;
        }
        
        /* Responsive slider width */
        .stSlider {
            width: 100%;
        }
        
        /* Responsive metric cards */
        .metric-card {
            min-height: 80px;
            padding: 1rem;
        }
        
        /* Responsive expander */
        .streamlit-expanderHeader {
            font-size: 0.95rem;
        }

        /* Top Navigation Buttons */
        .stButton > button {
            width: 100%;
            background: rgba(255, 255, 255, 0.15);
            color: #111;
            border: none;
            font-weight: 600;
            padding: 0.75rem 1rem;
            border-radius: 30px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            backdrop-filter: blur(10px);
        }

        .stButton > button:hover {
            background: rgba(255, 255, 255, 0.25);
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
        }

        .stButton > button:active {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            box-shadow: 0 8px 25px rgba(245, 87, 108, 0.4);
            transform: scale(1.05);
        }

        /* Primary Button Override */
        button[kind="primary"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.75rem 1.5rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }

        button[kind="primary"]:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4) !important;
        }

        /* Card Styling */
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }

        /* Custom Card */
        .custom-card {
            background: white;
            border-radius: 16px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.08);
            margin: 15px 0;
            border: 1px solid rgba(102, 126, 234, 0.1);
            transition: all 0.3s ease;
        }
        
        .custom-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 40px rgba(102, 126, 234, 0.15);
        }

        /* Metric Cards */
        div[data-testid="stMetricValue"] {
            font-size: 2.2rem;
            font-weight: 800;
            color: #2d3748;
        }

        div[data-testid="metric-container"] {
            background: linear-gradient(135deg, white 0%, rgba(240, 147, 251, 0.05) 100%);
            padding: 20px;
            border-radius: 16px;
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.08);
            border: 1px solid rgba(102, 126, 234, 0.1);
            transition: all 0.3s ease;
        }
        
        div[data-testid="metric-container"]:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 30px rgba(102, 126, 234, 0.15);
        }

        /* Headers with modern gradient */
        h1 {
            color: #2d3748;
            font-weight: 900;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            padding: 0.5rem 0;
            font-size: 2.5rem;
        }

        h2, h3 {
            color: #2d3748;
            font-weight: 800;
        }
        
        h2 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        /* Input fields styling */
        input, select, textarea {
            border-radius: 12px !important;
            border: 2px solid rgba(102, 126, 234, 0.2) !important;
            transition: all 0.3s ease !important;
        }

        input:focus, select:focus, textarea:focus {
            border-color: #667eea !important;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
        }

        /* Expander styling */
        .streamlit-expanderHeader {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(240, 147, 251, 0.05) 100%);
            border: 1px solid rgba(102, 126, 234, 0.2);
            border-radius: 12px;
            transition: all 0.3s ease;
        }

        .streamlit-expanderHeader:hover {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(240, 147, 251, 0.1) 100%);
        }

        /* Dataframe styling */
        .dataframe {
            border-collapse: collapse !important;
            border-radius: 12px !important;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        table {
            background: white;
            border-radius: 12px;
            overflow: hidden;
        }

        table thead {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        table tbody tr {
            border-bottom: 1px solid rgba(102, 126, 234, 0.1);
            transition: all 0.3s ease;
        }

        table tbody tr:hover {
            background: rgba(102, 126, 234, 0.05);
        }

        /* Success & Info messages */
        .stSuccess {
            background: linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(102, 255, 102, 0.05) 100%) !important;
            border-left: 4px solid #4CAF50 !important;
            border-radius: 12px !important;
            padding: 15px !important;
        }

        .stInfo {
            background: linear-gradient(135deg, rgba(33, 150, 243, 0.1) 0%, rgba(102, 204, 255, 0.05) 100%) !important;
            border-left: 4px solid #2196F3 !important;
            border-radius: 12px !important;
            padding: 15px !important;
        }

        .stWarning {
            background: linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 179, 102, 0.05) 100%) !important;
            border-left: 4px solid #ff9800 !important;
            border-radius: 12px !important;
            padding: 15px !important;
        }

        .stError {
            background: linear-gradient(135deg, rgba(244, 67, 54, 0.1) 0%, rgba(255, 102, 102, 0.05) 100%) !important;
            border-left: 4px solid #f44336 !important;
            border-radius: 12px !important;
            padding: 15px !important;
        }

        /* Slider styling */
        .stSlider > div {
            border-radius: 12px;
        }

        /* Checkbox styling */
        .stCheckbox {
            color: #2d3748;
        }

        /* ══════════════════════════════════════════════════════════════ */
        /* HEADER STYLES */
        /* ══════════════════════════════════════════════════════════════ */
        
        .header-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 25px 30px;
            border-radius: 20px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(102, 126, 234, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.2);
            position: relative;
            z-index: 10;
            border: 1px solid rgba(255, 255, 255, 0.15);
        }
        
        .app-title {
            color: #ffffff;
            font-size: 2.2rem;
            font-weight: 900;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
            position: relative;
            z-index: 1;
        }
        
        .app-tagline {
            color: #ffffff;
            font-size: 1.05rem;
            font-weight: 600;
            margin: 10px 0 0 0;
            background: rgba(255, 255, 255, 0.12);
            padding: 8px 16px;
            border-radius: 25px;
            display: inline-block;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            position: relative;
            z-index: 1;
        }
        
        .version-badge {
            background: linear-gradient(135deg, rgba(245, 87, 108, 0.9) 0%, rgba(240, 147, 251, 0.9) 100%);
            padding: 10px 20px;
            border-radius: 25px;
            color: #ffffff;
            font-weight: 700;
            font-size: 0.9rem;
            border: 1px solid rgba(255, 255, 255, 0.25);
            display: inline-block;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
            box-shadow: 0 6px 15px rgba(245, 87, 108, 0.2);
            position: relative;
            z-index: 1;
        }
        
        .user-info {
            text-align: right;
            padding-top: 4px;
            position: relative;
            z-index: 1;
        }
        
        .user-name {
            color: #ffffff;
            font-weight: 700;
            font-size: 0.95rem;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
            margin: 0;
        }
        
        .user-email {
            color: rgba(255, 255, 255, 0.85);
            font-size: 0.8rem;
            margin-top: 2px;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.15);
        }

        /* ══════════════════════════════════════════════════════════════ */
        /* NAVIGATION STYLES */
        /* ══════════════════════════════════════════════════════════════ */
        
        .nav-container {
            display: flex;
            gap: 8px;
            padding: 12px 20px;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.95) 0%, rgba(118, 75, 162, 0.95) 100%);
            border-radius: 50px;
            margin-bottom: 25px;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            flex-wrap: wrap;
            justify-content: center;
            border: 1px solid rgba(255, 255, 255, 0.15);
            position: relative;
            z-index: 100;
        }
        
        .nav-btn {
            padding: 10px 18px !important;
            border-radius: 30px !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            border: none !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            background: rgba(255, 255, 255, 0.12) !important;
            color: white !important;
            white-space: nowrap;
            cursor: pointer;
            position: relative;
            overflow: hidden;
            pointer-events: auto !important;
            z-index: 101;
        }
        
        .nav-btn:hover {
            background: rgba(255, 255, 255, 0.22) !important;
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15) !important;
        }
        
        .nav-btn.active {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
            box-shadow: 0 8px 25px rgba(245, 87, 108, 0.3) !important;
            transform: scale(1.05);
        }

        /* Responsive navigation */
        @media (max-width: 768px) {
            .nav-container {
                gap: 6px;
                padding: 10px 12px;
                justify-content: flex-start;
                overflow-x: auto;
            }
            .nav-btn {
                padding: 8px 14px !important;
                font-size: 0.8rem !important;
            }
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            h1 { font-size: 1.8rem; }
            h2 { font-size: 1.3rem; }
            h3 { font-size: 1rem; }
            
            .main .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
            
            div[data-testid="stMetricValue"] {
                font-size: 1.5rem;
            }
        }
    </style>
    """


def get_icon_mapping():
    """Return icon mapping for different sections"""
    return {
        'home': '🏠',
        'analysis': '📊',
        'screener': '🎯',
        'portfolio': '💼',
        'technical': '📈',
        'fundamental': '💰',
        'risk': '⚠️',
        'prediction': '🔮',
        'settings': '⚙️',
        'bullish': '🟢',
        'bearish': '🔴',
        'neutral': '🟡',
    }


def get_theme_css(dark_mode: bool = False) -> str:
    """Return theme-specific CSS for dark/light mode"""
    if dark_mode:
        return """
    <style>
        /* Dark mode: comprehensive theming */
        body, .stApp, .main, .block-container {
            background-color: #0f172a !important;
            color: #e2e8f0 !important;
        }

        /* Text elements */
        p, span, label, div, a, .stMarkdown, .stText, .stTextInput, .stButton > button {
            color: #e2e8f0 !important;
        }

        /* Links */
        a { color: #60a5fa !important; }

        /* Tables */
        table, thead, tbody, tr, th, td {
            color: #e2e8f0 !important;
            background-color: #1e293b !important;
            border-color: #334155 !important;
        }

        /* Cards and containers */
        .stContainer, .stBlock, .stBlock-container {
            background-color: #1e293b !important;
        }

        /* Metric cards */
        div[style*="background: white"] {
            background: #1e293b !important;
            border: 1px solid #334155 !important;
        }

        /* Info cards */
        div[style*="background: #bee3f8"] { background: #1e293b !important; border-left-color: #3b82f6 !important; }
        div[style*="background: #c6f6d5"] { background: #1e293b !important; border-left-color: #10b981 !important; }
        div[style*="background: #feebc8"] { background: #1e293b !important; border-left-color: #f59e0b !important; }
        div[style*="background: #fed7d7"] { background: #1e293b !important; border-left-color: #ef4444 !important; }

        /* Signal badges */
        span[style*="background: #c6f6d5"] { background: #1e293b !important; color: #10b981 !important; border: 1px solid #10b981 !important; }
        span[style*="background: #fed7d7"] { background: #1e293b !important; color: #ef4444 !important; border: 1px solid #ef4444 !important; }
        span[style*="background: #e2e8f0"] { background: #1e293b !important; color: #94a3b8 !important; border: 1px solid #94a3b8 !important; }

        /* Navigation and headers */
        .header-box, .nav-container {
            background: linear-gradient(135deg, #1e293b, #334155) !important;
            border-bottom: 1px solid #475569 !important;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #1e293b !important;
        }

        /* Input fields */
        .stTextInput input, .stSelectbox select, .stMultiselect select {
            background-color: #334155 !important;
            color: #e2e8f0 !important;
            border-color: #475569 !important;
        }

        /* Buttons */
        .stButton > button {
            background-color: #3b82f6 !important;
            color: white !important;
            border-color: #3b82f6 !important;
        }

        .stButton > button:hover {
            background-color: #2563eb !important;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #1e293b !important;
        }

        .stTabs [data-baseweb="tab"] {
            color: #94a3b8 !important;
        }

        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            color: #60a5fa !important;
            background-color: #334155 !important;
        }

        /* Expanders */
        .streamlit-expanderHeader {
            background-color: #334155 !important;
            color: #e2e8f0 !important;
        }

        /* Dataframes */
        .stDataFrame {
            background-color: #1e293b !important;
        }

        .stDataFrame table {
            background-color: #1e293b !important;
            color: #e2e8f0 !important;
        }

        /* Plot backgrounds */
        .js-plotly-plot .plotly .modebar {
            background-color: #1e293b !important;
        }
    </style>
        """
    else:
        return """
    <style>
        /* Light mode: comprehensive theming */
        body, .stApp, .main, .block-container {
            background-color: #ffffff !important;
            color: #1a202c !important;
        }

        /* Text elements */
        p, span, label, div, a, .stMarkdown, .stText, .stTextInput, .stButton > button {
            color: #1a202c !important;
        }

        /* Links */
        a { color: #1a73e8 !important; }

        /* Tables */
        table, thead, tbody, tr, th, td {
            color: #1a202c !important;
            background-color: #ffffff !important;
            border-color: #e2e8f0 !important;
        }

        /* Cards and containers */
        .stContainer, .stBlock, .stBlock-container {
            background-color: #ffffff !important;
        }

        /* Metric cards */
        div[style*="background: white"] {
            background: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
        }

        /* Info cards - keep original colors for light mode */
        div[style*="background: #bee3f8"] { background: #bee3f8 !important; }
        div[style*="background: #c6f6d5"] { background: #c6f6d5 !important; }
        div[style*="background: #feebc8"] { background: #feebc8 !important; }
        div[style*="background: #fed7d7"] { background: #fed7d7 !important; }

        /* Signal badges - keep original colors for light mode */
        span[style*="background: #c6f6d5"] { background: #c6f6d5 !important; }
        span[style*="background: #fed7d7"] { background: #fed7d7 !important; }
        span[style*="background: #e2e8f0"] { background: #e2e8f0 !important; }

        /* Navigation and headers */
        .header-box, .nav-container {
            background: linear-gradient(135deg, #667eea, #764ba2) !important;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #f8fafc !important;
        }

        /* Input fields */
        .stTextInput input, .stSelectbox select, .stMultiselect select {
            background-color: #ffffff !important;
            color: #1a202c !important;
            border-color: #d1d5db !important;
        }

        /* Buttons */
        .stButton > button {
            background-color: #667eea !important;
            color: white !important;
        }

        .stButton > button:hover {
            background-color: #5a67d8 !important;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #f8fafc !important;
        }

        .stTabs [data-baseweb="tab"] {
            color: #4a5568 !important;
        }

        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            color: #667eea !important;
            background-color: #ffffff !important;
        }

        /* Expanders */
        .streamlit-expanderHeader {
            background-color: #f8fafc !important;
            color: #1a202c !important;
        }

        /* Dataframes */
        .stDataFrame {
            background-color: #ffffff !important;
        }

        .stDataFrame table {
            background-color: #ffffff !important;
            color: #1a202c !important;
        }
    </style>
        """