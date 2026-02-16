#!/bin/bash
echo "🚀 Initializing AI Trading Lab..."
python SETUP.py
echo "✅ Setup complete!"
streamlit run app_modern.py --server.port=7860
