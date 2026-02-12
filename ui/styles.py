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

        /* ════════════════════════════════════════════════════════════ */
        /* MOBILE RESPONSIVENESS & ADAPTIVE LAYOUT */
        /* ════════════════════════════════════════════════════════════ */

        /* Tablet & Mobile (max-width: 768px) */
        @media (max-width: 768px) {
            /* Main content padding */
            .main .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }

            /* Navigation buttons - stack better on mobile */
            .stButton > button {
                padding: 0.6rem 0.8rem;
                font-size: 0.9rem;
            }

            /* Reduce header size on mobile */
            .header-box {
                padding: 20px 25px !important;
            }

            .app-title {
                font-size: 1.8rem !important;
            }

            .app-tagline {
                font-size: 0.85rem !important;
            }

            /* Responsive headings */
            h1 {
                font-size: 1.5rem;
                margin-bottom: 0.8rem;
            }

            h2 {
                font-size: 1.2rem;
                margin-bottom: 0.6rem;
            }

            h3 {
                font-size: 1rem;
                margin-bottom: 0.5rem;
            }

            /* Full width selectboxes and inputs */
            .stSelectbox,
            .stTextInput,
            .stNumberInput,
            .stTextArea {
                width: 100%;
            }

            /* Responsive metrics */
            [data-testid="metricContainer"] {
                min-width: 100%;
                padding: 0.8rem;
            }

            /* Responsive tabs */
            .stTabs [data-baseweb="tab-list"] button {
                font-size: 0.9rem;
                padding: 0.6rem 1rem;
            }

            /* Responsive dataframe */
            .stDataFrame {
                font-size: 0.85rem;
            }

            /* Responsive charts */
            .plotly-graph-div {
                height: 250px !important;
            }

            /* Expander mobile optimization */
            .streamlit-expanderHeader {
                font-size: 0.95rem;
                padding: 0.8rem;
            }

            /* Slider width */
            .stSlider {
                width: 100%;
            }

            /* Button full width */
            .stButton {
                width: 100%;
            }
        }

        /* Small Mobile (max-width: 480px) */
        @media (max-width: 480px) {
            /* Very small margins/padding */
            .main .block-container {
                padding-left: 0.8rem;
                padding-right: 0.8rem;
                padding-top: 1rem;
            }

            .main {
                padding: 0.5rem;
            }

            /* Header scaling */
            .header-box {
                padding: 15px 20px !important;
                margin-bottom: 15px;
            }

            .app-title {
                font-size: 1.4rem !important;
                letter-spacing: -0.3px;
            }

            .app-tagline {
                font-size: 0.75rem !important;
            }

            /* Smaller headings */
            h1 { font-size: 1.3rem; }
            h2 { font-size: 1.1rem; }
            h3 { font-size: 0.95rem; }

            /* Reduce button size */
            .stButton > button {
                padding: 0.5rem 0.6rem;
                font-size: 0.85rem;
                height: auto;
            }

            /* Stacked columns on very small screens */
            [data-testid="column"] {
                width: 100% !important;
                margin-bottom: 0.8rem;
            }

            /* Smaller metric cards */
            [data-testid="metricContainer"] {
                padding: 0.6rem;
            }

            /* Reduce tab font size */
            .stTabs [data-baseweb="tab-list"] button {
                font-size: 0.8rem;
                padding: 0.5rem 0.8rem;
            }

            /* Smaller charts */
            .plotly-graph-div {
                height: 200px !important;
            }

            /* Text area optimization */
            .stTextArea textarea {
                font-size: 0.9rem;
            }

            /* Smaller expanders */
            .streamlit-expanderHeader {
                font-size: 0.9rem;
                padding: 0.6rem;
            }

            /* Compact data display */
            .stDataFrame {
                font-size: 0.8rem;
            }
        }

        /* Landscape mode optimization */
        @media (max-height: 600px) {
            .main .block-container {
                padding-top: 1rem;
                padding-bottom: 1rem;
            }

            .header-box {
                padding: 15px 20px !important;
                margin-bottom: 10px;
            }
        }

        /* Large screens (max-width: 1200px) optimization */
        @media (min-width: 1200px) {
            .main .block-container {
                padding-left: 3rem;
                padding-right: 3rem;
            }
        }

        /* Dark mode support (optional) */
        @media (prefers-color-scheme: dark) {
            .main {
                background: #1a1a1e;
                color: #e0e0e0;
            }
            
            .stApp {
                background: #1a1a1e;
            }
            
            .stButton > button {
                background: #2d2d3d;
                color: #a0a0ff;
                border-color: #667eea;
            }
            
            .stButton > button:hover {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            
            .custom-card {
                background: #2d2d3d;
                color: #e0e0e0;
            }
            
            [data-testid="metric-container"] {
                background: #2d2d3d;
                color: #e0e0e0;
            }
            
            [data-testid="stMetricValue"] {
                color: #e0e0e0;
            }
            
            h1, h2, h3 {
                color: #e0e0e0;
            }
            
            .stTextInput>div>div>input {
                background: #2d2d3d;
                color: #e0e0e0;
                border-color: #667eea;
            }
            
            .stSelectbox > div > div {
                background: #2d2d3d;
                color: #e0e0e0;
            }
            
            .stTabs [data-baseweb="tab-list"] {
                background: #2d2d3d;
            }
            
            .stTabs [data-baseweb="tab"] {
                background: #1a1a1e;
                color: #e0e0e0;
            }
            
            .streamlit-expanderHeader {
                background: #2d2d3d;
                color: #e0e0e0;
                border-color: #667eea;
            }
            
            .stAlert {
                background: #2d2d3d;
                color: #e0e0e0;
            }
            
            .signal-bullish {
                background: #1a4d1a;
                color: #90ee90;
            }
            
            .signal-bearish {
                background: #4d1a1a;
                color: #ff9090;
            }
            
            .signal-neutral {
                background: #3d3d4d;
                color: #e0e0e0;
            }
            
            ::-webkit-scrollbar-track {
                background: #2d2d3d;
            }
            
            .version-badge {
                background: rgba(255, 255, 255, 0.15);
                color: #e0e0e0;
            }
            
            /* DataFrame dark mode */
            .dataframe {
                background: #2d2d3d;
                color: #e0e0e0;
            }
            
            /* Slider dark mode */
            .stSlider [data-baseweb="slider"] {
                background: #2d2d3d;
            }
            
            /* Checkbox dark mode */
            .stCheckbox label {
                color: #e0e0e0;
            }
            
            /* Radio button dark mode */
            .stRadio label {
                color: #e0e0e0;
            }
            
            /* Number input dark mode */
            .stNumberInput > div > div > input {
                background: #2d2d3d;
                color: #e0e0e0;
            }
            
            /* Text area dark mode */
            .stTextArea textarea {
                background: #2d2d3d;
                color: #e0e0e0;
            }
            
            /* Metric responsive dark mode */
            .metric-responsive {
                background: #2d2d3d;
                color: #e0e0e0;
            }
            
            /* Navigation bar dark mode */
            .nav-bar {
                background: linear-gradient(135deg, #4a4a6a 0%, #5a4a6a 100%);
            }
            
            /* Header styling dark mode */
            .header-box {
                background: #2d2d3d !important;
                color: #e0e0e0 !important;
            }
            
            .app-title {
                color: #e0e0e0 !important;
            }
            
            .app-tagline {
                color: #b0b0b0 !important;
            }
            
            /* Info, Warning, Success boxes dark mode */
            .stInfo {
                background: #1a2a3a;
                color: #90c0f0;
            }
            
            .stWarning {
                background: #3a3a2a;
                color: #f0d090;
            }
            
            .stSuccess {
                background: #1a3a2a;
                color: #90f090;
            }
            
            .stError {
                background: #3a1a1a;
                color: #f09090;
            }
            
            /* Progress bar dark mode */
            .stProgress > div > div > div > div {
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            }
        }
        
        /* Force dark mode when enabled in settings */
        .dark-mode {
            background: #1a1a1e !important;
            color: #e0e0e0 !important;
        }
        
        .dark-mode .stApp {
            background: #1a1a1e !important;
        }
        
        .dark-mode .main {
            background: #1a1a1e !important;
        }
        
        .dark-mode .custom-card,
        .dark-mode [data-testid="metric-container"],
        .dark-mode .stTextInput>div>div>input,
        .dark-mode .stSelectbox > div > div,
        .dark-mode .stTabs [data-baseweb="tab-list"],
        .dark-mode .streamlit-expanderHeader,
        .dark-mode .stAlert,
        .dark-mode .stNumberInput > div > div > input,
        .dark-mode .stTextArea textarea,
        .dark-mode .metric-responsive,
        .dark-mode .header-box {
            background: #2d2d3d !important;
            color: #e0e0e0 !important;
        }
        
        .dark-mode h1, .dark-mode h2, .dark-mode h3,
        .dark-mode [data-testid="stMetricValue"],
        .dark-mode .stCheckbox label,
        .dark-mode .stRadio label {
            color: #e0e0e0 !important;
        }
        
        .dark-mode .stButton > button {
            background: #2d2d3d;
            color: #a0a0ff;
            border-color: #667eea;
        }
        
        .dark-mode .stButton > button:hover {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        /* Responsive metric card styling */
        .metric-responsive {
            padding: 1rem;
            border-radius: 8px;
            background: white;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
            transition: transform 0.2s ease;
        }

        .metric-responsive:active {
            transform: scale(0.98);
        }

        /* Touch-friendly buttons */
        @media (any-hover: none) {
            .stButton > button {
                min-height: 44px;
            }

            .stSelectbox > div > div > div {
                min-height: 44px;
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
        'buy': '✅',
        'sell': '❌',
        'hold': '⏸️'
    }

