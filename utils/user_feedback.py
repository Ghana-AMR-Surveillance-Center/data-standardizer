"""
Enhanced user feedback and notification system
"""

import streamlit as st
import time
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UserFeedback:
    """
    Enhanced user feedback and notification system
    """
    
    def __init__(self):
        self.notifications = []
        self.progress_tasks = {}
    
    def show_success(self, message: str, duration: int = 3, icon: str = "✅"):
        """Show success message with auto-dismiss"""
        st.success(f"{icon} {message}")
        
        # Auto-dismiss after duration
        if duration > 0:
            time.sleep(duration)
            st.empty()
    
    def show_info(self, message: str, duration: int = 5, icon: str = "ℹ️"):
        """Show info message with auto-dismiss"""
        st.info(f"{icon} {message}")
        
        if duration > 0:
            time.sleep(duration)
            st.empty()
    
    def show_warning(self, message: str, duration: int = 7, icon: str = "⚠️"):
        """Show warning message with auto-dismiss"""
        st.warning(f"{icon} {message}")
        
        if duration > 0:
            time.sleep(duration)
            st.empty()
    
    def show_error(self, message: str, error_id: str = None, duration: int = 0, icon: str = "❌"):
        """Show error message with optional error ID"""
        error_msg = f"{icon} {message}"
        if error_id:
            error_msg += f"\n\n**Error ID:** `{error_id}`"
        
        st.error(error_msg)
        
        if duration > 0:
            time.sleep(duration)
            st.empty()
    
    def show_progress_bar(self, task_id: str, message: str = "Processing..."):
        """Show progress bar for long-running tasks"""
        self.progress_tasks[task_id] = {
            'message': message,
            'start_time': time.time(),
            'progress': 0
        }
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        return progress_bar, status_text
    
    def update_progress(self, task_id: str, progress: float, message: str = None):
        """Update progress bar"""
        if task_id not in self.progress_tasks:
            return
        
        self.progress_tasks[task_id]['progress'] = progress
        
        if message:
            self.progress_tasks[task_id]['message'] = message
    
    def complete_progress(self, task_id: str, message: str = "Completed!"):
        """Complete progress bar"""
        if task_id in self.progress_tasks:
            del self.progress_tasks[task_id]
        
        st.success(f"✅ {message}")
    
    def show_loading_spinner(self, message: str = "Loading..."):
        """Show loading spinner"""
        with st.spinner(message):
            pass
    
    def show_notification(self, title: str, message: str, type: str = "info", 
                         duration: int = 5, persistent: bool = False):
        """Show notification with title and message"""
        notification = {
            'id': f"notif_{int(time.time())}",
            'title': title,
            'message': message,
            'type': type,
            'timestamp': datetime.now(),
            'duration': duration,
            'persistent': persistent
        }
        
        self.notifications.append(notification)
        
        # Display notification
        if type == "success":
            st.success(f"**{title}**\n\n{message}")
        elif type == "error":
            st.error(f"**{title}**\n\n{message}")
        elif type == "warning":
            st.warning(f"**{title}**\n\n{message}")
        else:
            st.info(f"**{title}**\n\n{message}")
        
        # Auto-dismiss if not persistent
        if not persistent and duration > 0:
            time.sleep(duration)
            st.empty()
    
    def show_data_summary(self, df, title: str = "Data Summary"):
        """Show comprehensive data summary"""
        with st.expander(f"📊 {title}", expanded=False):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Rows", len(df))
            
            with col2:
                st.metric("Columns", len(df.columns))
            
            with col3:
                null_percentage = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
                st.metric("Missing Data", f"{null_percentage:.1f}%")
            
            with col4:
                memory_usage = df.memory_usage(deep=True).sum() / 1024 / 1024
                st.metric("Memory (MB)", f"{memory_usage:.1f}")
    
    def show_operation_status(self, operation: str, status: str, details: str = ""):
        """Show operation status with details"""
        status_icons = {
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️',
            'processing': '⏳'
        }
        
        icon = status_icons.get(status, 'ℹ️')
        
        if details:
            st.write(f"{icon} **{operation}**: {status.title()}")
            st.caption(details)
        else:
            st.write(f"{icon} **{operation}**: {status.title()}")
    
    def show_help_tooltip(self, help_text: str, icon: str = "❓"):
        """Show help tooltip"""
        st.markdown(f"""
        <div style="position: relative; display: inline-block;">
            <span style="cursor: help; color: #666;">{icon}</span>
            <div style="position: absolute; bottom: 100%; left: 50%; transform: translateX(-50%); 
                        background: #333; color: white; padding: 8px; border-radius: 4px; 
                        font-size: 12px; white-space: nowrap; z-index: 1000; 
                        opacity: 0; transition: opacity 0.3s;">
                {help_text}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def show_feature_highlight(self, feature: str, description: str, 
                             action_text: str = "Try it now!"):
        """Show feature highlight with call-to-action"""
        st.info(f"""
        🎯 **{feature}**
        
        {description}
        
        *{action_text}*
        """)
    
    def show_tips(self, tips: List[str], title: str = "💡 Tips"):
        """Show helpful tips"""
        with st.expander(title, expanded=False):
            for i, tip in enumerate(tips, 1):
                st.write(f"{i}. {tip}")
    
    def show_workflow_guide(self, steps: List[Dict[str, str]], current_step: int = 0, background_color: Optional[str] = None):
        """Show workflow guide with current step highlighted"""
        st.markdown("### 📋 Workflow Guide")
        
        for i, step in enumerate(steps):
            status_icon = "✅" if i < current_step else "⏳" if i == current_step else "⭕"
            status_color = "#28a745" if i < current_step else "#007bff" if i == current_step else "#6c757d"
            
            # Use provided background color or default
            step_bg = background_color if background_color else ('#f8f9fa' if i == current_step else '#ffffff')
            text_color = "#ffffff" if background_color == "#000000" else "#000000"
            desc_color = "#cccccc" if background_color == "#000000" else "#666"
            
            st.markdown(f"""
            <div style="padding: 10px; margin: 5px 0; border-left: 4px solid {status_color}; 
                        background: {step_bg}; color: {text_color};">
                <strong>{status_icon} Step {i+1}: {step['title']}</strong><br>
                <span style="color: {desc_color}; font-size: 0.9em;">{step['description']}</span>
            </div>
            """, unsafe_allow_html=True)
    
    def clear_all_notifications(self):
        """Clear all notifications"""
        self.notifications.clear()
        st.rerun()

# Global user feedback instance
user_feedback = UserFeedback()
