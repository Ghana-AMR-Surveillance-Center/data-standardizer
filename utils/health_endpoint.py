"""
Health check endpoint for Streamlit app
"""

import streamlit as st
from utils.health_monitor import HealthMonitor
from config.production import production_config

def render_health_page():
    """Render health monitoring page"""
    st.title("🏥 System Health Monitor")
    st.markdown("---")
    
    # Initialize health monitor
    if 'health_monitor' not in st.session_state:
        st.session_state['health_monitor'] = HealthMonitor()
    
    monitor = st.session_state['health_monitor']
    
    # Get health status
    health = monitor.get_health_summary()
    
    # Status indicator
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Status", health['status'])
    
    with col2:
        st.metric("Uptime", health['uptime'])
    
    with col3:
        success_rate = health['application']['success_rate']
        st.metric("Success Rate", success_rate)
    
    # System metrics
    st.subheader("📊 System Metrics")
    sys_col1, sys_col2, sys_col3 = st.columns(3)
    
    with sys_col1:
        st.metric("CPU Usage", health['system']['cpu'])
    
    with sys_col2:
        st.metric("Memory Usage", health['system']['memory'])
    
    with sys_col3:
        st.metric("Disk Usage", health['system']['disk'])
    
    # Application metrics
    st.subheader("📈 Application Metrics")
    app_col1, app_col2, app_col3 = st.columns(3)
    
    with app_col1:
        st.metric("Total Requests", health['application']['total_requests'])
    
    with app_col2:
        st.metric("Success Rate", health['application']['success_rate'])
    
    with app_col3:
        st.metric("Avg Processing Time", health['application']['avg_processing_time'])
    
    # Warnings
    if health['warnings']:
        st.subheader("⚠️ Warnings")
        for warning in health['warnings']:
            st.warning(warning)
    
    # Refresh button
    if st.button("🔄 Refresh Health Status"):
        st.rerun()
    
    # Detailed health data
    with st.expander("🔍 Detailed Health Data"):
        detailed_health = monitor.get_system_health()
        st.json(detailed_health)

