"""
Navigation and Page Routing Module for TradeGenius AI
======================================================
Centralized page routing and navigation management.

This module handles:
- Page routing logic
- Navigation state management
- Page loader functions
- Route validation
"""

import streamlit as st
from typing import Dict, Callable, Any
import logging

logger = logging.getLogger(__name__)


class PageRouter:
    """
    Centralized page routing system for the AI Trading Lab
    """

    def __init__(self):
        self._routes: Dict[str, Callable] = {}
        self._page_metadata: Dict[str, Dict[str, Any]] = {}

    def register_page(self, page_name: str, handler: Callable,
                     metadata: Dict[str, Any] = None) -> None:
        """
        Register a page handler

        Args:
            page_name: Name of the page (must match sidebar selection)
            handler: Function to call when page is selected
            metadata: Optional metadata about the page
        """
        self._routes[page_name] = handler
        self._page_metadata[page_name] = metadata or {}

    def get_available_pages(self) -> list:
        """Get list of all registered pages"""
        return list(self._routes.keys())

    def route_to_page(self, page_name: str, *args, **kwargs) -> None:
        """
        Route to a specific page

        Args:
            page_name: Name of the page to route to
            *args, **kwargs: Arguments to pass to the page handler
        """
        if page_name in self._routes:
            try:
                logger.info(f"Routing to page: {page_name}")
                self._routes[page_name](*args, **kwargs)
            except Exception as e:
                logger.error(f"Error routing to page {page_name}: {e}")
                st.error(f"Error loading page {page_name}: {str(e)}")
        else:
            logger.warning(f"Unknown page requested: {page_name}")
            st.error(f"Page '{page_name}' not found")

    def get_page_metadata(self, page_name: str) -> Dict[str, Any]:
        """Get metadata for a specific page"""
        return self._page_metadata.get(page_name, {})


# Global router instance
page_router = PageRouter()


def register_app_pages():
    """
    Register all application pages with the router
    This function should be called once during app initialization
    """
    # Import page handlers here to avoid circular imports
    page_imports = {
        "🏠 Home": ('pages.home', 'render_home_page'),
        "📊 Stock Analysis": ('pages.analysis', 'render_stock_analysis'),
        "🤖 AI Deep Analysis": ('pages.ai', 'render_ai'),
        "🎯 Smart Screener": ('pages.screener', 'render_smart_screener'),
        "📰 General News": ('pages.news', 'render_general_news'),
        "💼 Portfolio Manager": ('pages.portfolio', 'render_portfolio_manager'),
        "🔬 Deep Learning": ('pages.deep_learning', 'render_deep_learning'),
        "📈 Strategy Backtest": ('pages.backtest', 'render_strategy_backtest'),
        "👤 My Profile": ('pages.profile', 'render_my_profile'),
        "🔐 Security Settings": ('pages.security', 'render_security_settings'),
        "⚙️ Account Settings": ('pages.account', 'render_account_settings'),
        "📊 Zerodha Portfolio": ('pages.zerodha_portfolio', 'render_zerodha_portfolio'),
        "🔬 Zerodha Analyze": ('pages.zerodha_analyze', 'render_zerodha_analyze'),
        "🔁 Zerodha Trade": ('pages.zerodha_trade', 'render_zerodha_trade'),
        "⚙️ Settings": ('pages.settings', 'render_settings'),
    }

    # Register all pages
    page_metadata = {
        "🏠 Home": {"category": "main", "requires_auth": False, "description": "Welcome dashboard and overview"},
        "📊 Stock Analysis": {"category": "analysis", "requires_auth": False, "description": "Technical and fundamental analysis"},
        "🤖 AI Deep Analysis": {"category": "analysis", "requires_auth": False, "description": "Advanced AI-powered analysis"},
        "🎯 Smart Screener": {"category": "analysis", "requires_auth": False, "description": "Stock screening with ML models"},
        "📰 General News": {"category": "information", "requires_auth": False, "description": "Market news and updates"},
        "💼 Portfolio Manager": {"category": "portfolio", "requires_auth": True, "description": "Portfolio management and optimization"},
        "🔬 Deep Learning": {"category": "advanced", "requires_auth": False, "description": "Deep learning model training"},
        "📈 Strategy Backtest": {"category": "advanced", "requires_auth": False, "description": "Strategy backtesting and validation"},
        "👤 My Profile": {"category": "user", "requires_auth": True, "description": "User profile management"},
        "🔐 Security Settings": {"category": "user", "requires_auth": True, "description": "Security and authentication settings"},
        "⚙️ Account Settings": {"category": "user", "requires_auth": True, "description": "Account configuration"},
        "📊 Zerodha Portfolio": {"category": "zerodha", "requires_auth": True, "description": "Zerodha portfolio integration"},
        "🔬 Zerodha Analyze": {"category": "zerodha", "requires_auth": True, "description": "Zerodha portfolio analysis"},
        "🔁 Zerodha Trade": {"category": "zerodha", "requires_auth": True, "description": "Zerodha automated trading"},
        "⚙️ Settings": {"category": "system", "requires_auth": False, "description": "Application settings"},
    }

    for page_name, (module_name, func_name) in page_imports.items():
        try:
            module = __import__(module_name, fromlist=[func_name])
            handler = getattr(module, func_name)
            metadata = page_metadata.get(page_name, {})
            page_router.register_page(page_name, handler, metadata)
            logger.info(f"Registered page: {page_name}")
        except Exception as e:
            logger.warning(f"Failed to register page {page_name}: {e}")
            # Register a placeholder handler
            def placeholder_handler(*args, **kwargs):
                st.info(f"🚧 {page_name} is under development.")
            page_router.register_page(page_name, placeholder_handler, page_metadata.get(page_name, {}))

    logger.info(f"Registered {len(page_router.get_available_pages())} pages")


def get_page_sidebar_options() -> list:
    """
    Get the list of pages to display in the sidebar
    Organized by categories for better UX
    """
    page_categories = {
        "main": ["🏠 Home"],
        "analysis": ["📊 Stock Analysis", "🤖 AI Deep Analysis", "🎯 Smart Screener"],
        "information": ["📰 General News"],
        "portfolio": ["💼 Portfolio Manager"],
        "advanced": ["🔬 Deep Learning", "📈 Strategy Backtest"],
        "user": ["👤 My Profile", "🔐 Security Settings", "⚙️ Account Settings"],
        "zerodha": ["📊 Zerodha Portfolio", "🔬 Zerodha Analyze", "🔁 Zerodha Trade"],
        "system": ["⚙️ Settings"]
    }

    sidebar_options = []

    # Add pages by category
    for category, pages in page_categories.items():
        # Add category header (except for main)
        if category != "main":
            sidebar_options.append(f"─── {category.upper()} ───")

        # Add pages in this category
        sidebar_options.extend(pages)

    return sidebar_options


def render_page_with_router(page: str, *args, **kwargs) -> None:
    """
    Render a page using the router system

    Args:
        page: Page name to render
        *args, **kwargs: Arguments to pass to the page handler
    """
    # Check if router is initialized
    if not page_router.get_available_pages():
        register_app_pages()

    # Route to the requested page
    page_router.route_to_page(page, *args, **kwargs)


def get_page_info(page_name: str) -> Dict[str, Any]:
    """
    Get information about a specific page

    Args:
        page_name: Name of the page

    Returns:
        Dict with page metadata
    """
    return page_router.get_page_metadata(page_name)


def validate_page_access(page_name: str, user_authenticated: bool = False) -> bool:
    """
    Check if user can access a specific page

    Args:
        page_name: Name of the page
        user_authenticated: Whether user is authenticated

    Returns:
        True if access is allowed, False otherwise
    """
    metadata = page_router.get_page_metadata(page_name)

    if metadata.get("requires_auth", False) and not user_authenticated:
        return False

    return True