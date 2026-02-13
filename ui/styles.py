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

        /* Main App Styling with Modern Background */
        .main {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 1rem;
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
