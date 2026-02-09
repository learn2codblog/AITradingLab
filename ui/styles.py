"""
Modern UI Styles and Theme Configuration
"""

def get_custom_css():
    """Return custom CSS for modern UI styling"""
    return """
    <style>
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

        /* Main App Styling */
        .main {
            background: #f8f9fa;
            padding: 1rem;
        }

        /* Top Navigation Buttons */
        .stButton > button {
            width: 100%;
            background: white;
            color: #667eea;
            border: 2px solid #667eea;
            font-weight: 600;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            transition: all 0.3s ease;
        }

        .stButton > button:hover {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-color: #667eea;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }

        /* Primary Button Override */
        button[kind="primary"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
        }

        button[kind="primary"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5) !important;
        }

        /* Card Styling */
        .stApp {
            background: #f8f9fa;
        }

        /* Custom Card */
        .custom-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin: 15px 0;
            border-left: 5px solid #667eea;
        }

        /* Metric Cards */
        div[data-testid="stMetricValue"] {
            font-size: 2rem;
            font-weight: 700;
            color: #2d3748;
        }

        div[data-testid="metric-container"] {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-top: 4px solid #667eea;
        }

        /* Headers */
        h1 {
            color: #2d3748;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            padding: 0.5rem 0;
        }

        h2, h3 {
            color: #4a5568;
            font-weight: 700;
            margin-top: 1.5rem;
        }

        /* Input Fields */
        .stTextInput>div>div>input {
            border-radius: 8px;
            border: 2px solid #e2e8f0;
            padding: 0.75rem;
        }

        .stTextInput>div>div>input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        /* Select boxes */
        .stSelectbox > div > div {
            border-radius: 8px;
            border: 2px solid #e2e8f0;
        }

        /* Number inputs */
        .stNumberInput > div > div > input {
            border-radius: 8px;
            border: 2px solid #e2e8f0;
        }

        /* DataFrames */
        .dataframe {
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: white;
            padding: 10px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 600;
            background: #f7fafc;
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        /* Info/Warning/Success Boxes */
        .stAlert {
            border-radius: 10px;
            border-left: 5px solid;
        }

        /* Progress Bar */
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        }

        /* Expander */
        .streamlit-expanderHeader {
            background: white;
            border-radius: 10px;
            font-weight: 600;
            color: #2d3748;
            border: 2px solid #e2e8f0;
        }

        .streamlit-expanderHeader:hover {
            border-color: #667eea;
        }

        /* Signal Badges */
        .signal-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            margin: 5px;
        }

        .signal-bullish {
            background: #c6f6d5;
            color: #22543d;
        }

        .signal-bearish {
            background: #fed7d7;
            color: #742a2a;
        }

        .signal-neutral {
            background: #e2e8f0;
            color: #2d3748;
        }

        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }

        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }

        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #764ba2;
        }

        /* Remove top padding */
        .block-container {
            padding-top: 2rem;
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
        'buy': '✅',
        'sell': '❌',
        'hold': '⏸️'
    }

