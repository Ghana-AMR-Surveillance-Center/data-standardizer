"""
Enhanced UI components for improved user experience
"""

import streamlit as st
from typing import List, Dict, Optional, Any
import time


class UIComponents:
    """Enhanced UI components for better user experience"""
    
    @staticmethod
    def workflow_card(title: str, description: str, icon: str, features: List[str], 
                     button_label: str, button_key: str, recommended: bool = False):
        """
        Create a modern workflow selection card using Streamlit native components.
        
        Args:
            title: Card title
            description: Card description
            icon: Icon emoji
            features: List of features
            button_label: Button label
            button_key: Unique button key
            recommended: Whether to show as recommended
        """
        with st.container():
            # Recommended badge or invisible placeholder - keeps card heights uniform
            if recommended:
                st.markdown(
                    "<span style='display:inline-block;background:linear-gradient(135deg,#667eea,#764ba2);"
                    "color:white;padding:0.2rem 0.6rem;border-radius:20px;font-size:0.75rem;"
                    "font-weight:600;margin-bottom:0.5rem'>⭐ Recommended</span>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown("<span style='visibility:hidden;display:block;line-height:1.8;font-size:0.75rem'>⭐</span>", unsafe_allow_html=True)
            
            # Icon and title - clear hierarchy
            st.markdown(f"### {icon} {title}")
            
            # Description - concise and scannable
            st.caption(description)
            st.markdown("")
            
            # Features list - easy to scan with checkmarks
            st.markdown("**Features:**")
            for feature in features:
                st.markdown(f"• {feature}")
            
            st.markdown("---")
            
            # Primary action - prominent button
            if st.button(button_label, key=button_key, use_container_width=True, 
                        type="primary" if recommended else "secondary"):
                return True
        return False
    
    @staticmethod
    def step_indicator(steps: List[Dict[str, Any]], current_step: int, 
                      completed_steps: Optional[List[int]] = None):
        """
        Create a visual step indicator using Streamlit native components.
        
        Args:
            steps: List of step dictionaries with 'title' and optional 'icon'
            current_step: Current step index (0-based)
            completed_steps: List of completed step indices
        """
        if completed_steps is None:
            completed_steps = list(range(current_step))
        
        # Create columns for steps
        cols = st.columns(len(steps))
        
        for i, step in enumerate(steps):
            with cols[i]:
                icon = step.get('icon', '')
                title = step.get('title', f'Step {i + 1}')
                
                # Determine status and styling
                if i in completed_steps:
                    status_icon = "✅"
                    badge_style = "background:#e6fffa;color:#047857;padding:0.25rem 0.5rem;border-radius:6px;font-weight:600"
                elif i == current_step:
                    status_icon = icon if icon else "⏳"
                    badge_style = "background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:0.25rem 0.5rem;border-radius:6px;font-weight:600"
                else:
                    status_icon = str(i + 1)
                    badge_style = "background:#f1f5f9;color:#64748b;padding:0.25rem 0.5rem;border-radius:6px;font-weight:600"
                
                st.markdown(
                    f"<span style='{badge_style}'>{status_icon} {title}</span>",
                    unsafe_allow_html=True
                )
    
    @staticmethod
    def info_banner(message: str, type: str = "info", icon: Optional[str] = None, 
                   dismissible: bool = False):
        """
        Create a styled info banner using Streamlit native components.
        
        Args:
            message: Banner message
            type: Banner type (info, success, warning, error)
            icon: Optional icon emoji
            dismissible: Whether banner can be dismissed (not implemented)
        """
        type_config = {
            "info": {"icon": "ℹ️"},
            "success": {"icon": "✅"},
            "warning": {"icon": "⚠️"},
            "error": {"icon": "❌"}
        }
        
        config = type_config.get(type, type_config["info"])
        display_icon = icon or config["icon"]
        
        # Use Streamlit's native components
        if type == "success":
            st.success(f"{display_icon} {message}")
        elif type == "warning":
            st.warning(f"{display_icon} {message}")
        elif type == "error":
            st.error(f"{display_icon} {message}")
        else:
            st.info(f"{display_icon} {message}")
    
    @staticmethod
    def quick_action_button(label: str, icon: str, key: str, help_text: str = "", 
                           type: str = "secondary"):
        """
        Create a quick action button with icon.
        
        Args:
            label: Button label
            icon: Icon emoji
            key: Unique key
            help_text: Help tooltip
            type: Button type
        """
        return st.button(f"{icon} {label}", key=key, help=help_text, type=type)
    
    @staticmethod
    def metric_card(title: str, value: Any, delta: Optional[str] = None, 
                   icon: Optional[str] = None, help_text: Optional[str] = None):
        """
        Create a styled metric card.
        
        Args:
            title: Metric title
            value: Metric value
            delta: Optional delta/change indicator
            icon: Optional icon
            help_text: Optional help text
        """
        icon_html = f'<span style="font-size: 1.5rem; margin-right: 8px;">{icon}</span>' if icon else ''
        help_html = f'<span title="{help_text}" style="cursor: help;">❓</span>' if help_text else ''
        
        st.metric(
            label=f"{icon_html}{title} {help_html}",
            value=value,
            delta=delta
        )
    
    @staticmethod
    def section_header(title: str, icon: str = "", description: str = "", 
                      collapsible: bool = False):
        """
        Create a styled section header with clear visual hierarchy.
        
        Args:
            title: Section title
            icon: Optional icon
            description: Optional description
            collapsible: Whether section is collapsible
        """
        icon_html = f"{icon} " if icon else ""
        
        if description:
            st.markdown(f"### {icon_html}{title}")
            st.caption(description)
        else:
            st.markdown(f"### {icon_html}{title}")
        
        st.markdown("---")
    
    @staticmethod
    def status_badge(status: str, size: str = "medium"):
        """
        Create a status badge using Streamlit native components.
        
        Args:
            status: Status text
            size: Badge size (small, medium, large) - not used, kept for compatibility
        """
        status_icons = {
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "info": "ℹ️",
            "pending": "⏳"
        }
        
        icon = status_icons.get(status.lower(), "⭕")
        st.markdown(f"**{icon} {status.title()}**")

# Global UI components instance
ui_components = UIComponents()

