import os
import re
from pathlib import Path
from datetime import datetime

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QTextEdit, QFileDialog, QMessageBox, QFrame, QSizePolicy, QApplication
)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QColor, QFont, QTextOption


class LogViewer(QDialog):
    """
    A dialog to view and filter application log files using PyQt6.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.log_dir = Path('logs')
        self.log_dir.mkdir(exist_ok=True)
        self.current_log_file = None
        self.log_levels = ['ALL', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        self.current_level = 'ALL'
        self.auto_refresh = True
        self.refresh_interval = 5000  # 5 seconds
        
        self.setup_ui()
        self.apply_dark_theme()
        self.load_log_files()
        
        # Set up auto-refresh timer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_logs)
        self.refresh_timer.start(self.refresh_interval)
    
    def setup_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('Log Viewer')
        self.setMinimumSize(900, 600)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Control frame
        control_frame = QFrame()
        control_layout = QHBoxLayout(control_frame)
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.setSpacing(10)
        
        # Log file selection
        control_layout.addWidget(QLabel('Log File:'))
        
        self.file_combo = QComboBox()
        self.file_combo.setMinimumWidth(300)
        self.file_combo.currentIndexChanged.connect(self.on_file_select)
        control_layout.addWidget(self.file_combo)
        
        # Log level filter
        control_layout.addWidget(QLabel('Log Level:'))
        
        self.level_combo = QComboBox()
        self.level_combo.addItems(self.log_levels)
        self.level_combo.setCurrentText('ALL')
        self.level_combo.currentTextChanged.connect(self.on_level_select)
        control_layout.addWidget(self.level_combo)
        
        # Refresh button
        self.refresh_btn = QPushButton('⟳')
        self.refresh_btn.setFixedWidth(30)
        self.refresh_btn.setToolTip('Refresh logs')
        self.refresh_btn.clicked.connect(self.refresh_logs)
        control_layout.addWidget(self.refresh_btn)
        
        # Auto-refresh toggle
        self.auto_refresh_btn = QPushButton('Auto-refresh: ON')
        self.auto_refresh_btn.setCheckable(True)
        self.auto_refresh_btn.setChecked(True)
        self.auto_refresh_btn.toggled.connect(self.toggle_auto_refresh)
        control_layout.addWidget(self.auto_refresh_btn)
        
        control_layout.addStretch()
        
        # Add control frame to main layout
        main_layout.addWidget(control_frame)
        
        # Log text area
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.text_edit.setFont(QFont('Consolas', 10))
        
        # Set monospace font with better line spacing
        font = self.text_edit.font()
        font.setStyleHint(QFont.StyleHint.TypeWriter)
        self.text_edit.setFont(font)
        
        # Configure text options for better readability
        text_options = QTextOption()
        text_options.setTabStopDistance(40)  # 40 pixels
        self.text_edit.document().setDefaultTextOption(text_options)
        
        main_layout.addWidget(self.text_edit)
        
        # Button frame
        btn_frame = QFrame()
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        
        # Save button
        self.save_btn = QPushButton('Save As...')
        self.save_btn.clicked.connect(self.save_log)
        btn_layout.addWidget(self.save_btn)
        
        # Clear button
        self.clear_btn = QPushButton('Clear Log')
        self.clear_btn.clicked.connect(self.clear_log)
        btn_layout.addWidget(self.clear_btn)
        
        btn_layout.addStretch()
        
        # Close button
        self.close_btn = QPushButton('Close')
        self.close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.close_btn)
        
        main_layout.addWidget(btn_frame)
        
        # Status bar
        self.status_bar = QLabel('Ready')
        self.status_bar.setStyleSheet('color: #888888; font-style: italic;')
        main_layout.addWidget(self.status_bar)
    
    def apply_dark_theme(self):
        """Apply a dark theme to the log viewer."""
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #e0e0e0;
            }
            
            QLabel {
                color: #e0e0e0;
            }
            
            QTextEdit {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 5px;
                selection-background-color: #3d3d3d;
                selection-color: #ffffff;
            }
            
            QComboBox, QPushButton {
                background-color: #3c3f41;
                color: #e0e0e0;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 5px 10px;
                min-width: 80px;
            }
            
            QComboBox:hover, QPushButton:hover {
                background-color: #4e5254;
                border-color: #6c7072;
            }
            
            QComboBox:on {
                background-color: #4e5254;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QComboBox::down-arrow {
                image: url(none);
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #e0e0e0;
            }
            
            QComboBox QAbstractItemView {
                background-color: #3c3f41;
                color: #e0e0e0;
                selection-background-color: #4e5254;
                border: 1px solid #555555;
                padding: 5px;
            }
            
            QScrollBar:vertical {
                border: none;
                background: #2b2b2b;
                width: 12px;
                margin: 0;
            }
            
            QScrollBar::handle:vertical {
                background: #4e5254;
                border-radius: 6px;
                min-height: 20px;
                margin: 3px;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
            
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
    
    def load_log_files(self):
        """Load available log files from the logs directory."""
        self.file_combo.clear()
        
        try:
            log_files = sorted(
                [f for f in self.log_dir.glob('*.log') if f.is_file()],
                key=os.path.getmtime,
                reverse=True
            )
            
            if not log_files:
                self.status_bar.setText('No log files found in logs directory')
                return
                
            self.file_combo.addItems([f.name for f in log_files])
            self.current_log_file = log_files[0] if log_files else None
            self.load_log_content()
            
        except Exception as e:
            self.status_bar.setText(f'Error loading log files: {str(e)}')
    
    def load_log_content(self):
        """Load the content of the selected log file with the current filters."""
        if not self.current_log_file or not self.current_log_file.exists():
            self.status_bar.setText('Log file not found')
            return
            
        try:
            self.text_edit.clear()
            
            with open(self.current_log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    self._process_log_line(line.strip())
                    
            self.status_bar.setText(f'Loaded {self.current_log_file.name}')
            
            # Scroll to bottom
            cursor = self.text_edit.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.text_edit.setTextCursor(cursor)
            
        except Exception as e:
            self.status_bar.setText(f'Error loading log file: {str(e)}')
    
    def _process_log_line(self, line):
        """Process a single log line and add it to the text area with appropriate formatting."""
        if not line.strip():
            return
            
        log_level = 'INFO'  # Default log level
        
        # Try to extract log level from the line
        level_match = re.search(r'\[(DEBUG|INFO|WARNING|ERROR|CRITICAL)\]', line)
        if level_match:
            log_level = level_match.group(1)
        
        # Skip if log level doesn't match the filter
        if self.current_level != 'ALL' and log_level != self.current_level:
            return
        
        # Create text format based on log level
        format = QTextCharFormat()
        
        # Set color based on log level
        if log_level == 'DEBUG':
            format.setForeground(QColor('#888888'))  # Gray
        elif log_level == 'INFO':
            format.setForeground(QColor('#e0e0e0'))  # Light gray
        elif log_level == 'WARNING':
            format.setForeground(QColor('#ffcc00'))  # Yellow
        elif log_level == 'ERROR':
            format.setForeground(QColor('#ff6b6b'))  # Red
        elif log_level == 'CRITICAL':
            format.setForeground(QColor('#ffffff'))  # White
            format.setBackground(QColor('#ff0000'))  # Red background
        
        # Add the line to the text edit
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        # Apply formatting
        cursor.insertText(line + '\n', format)
    
    def on_file_select(self, index):
        """Handle log file selection from dropdown."""
        if index >= 0:
            selected_file = self.file_combo.currentText()
            if selected_file:
                self.current_log_file = self.log_dir / selected_file
                self.load_log_content()
    
    def on_level_select(self, level):
        """Handle log level filter selection."""
        self.current_level = level
        if self.current_log_file:
            self.load_log_content()
    
    def toggle_auto_refresh(self, enabled):
        """Toggle auto-refresh of log content."""
        self.auto_refresh = enabled
        self.auto_refresh_btn.setText('Auto-refresh: ' + ('ON' if enabled else 'OFF'))
        
        if enabled:
            self.refresh_timer.start(self.refresh_interval)
        else:
            self.refresh_timer.stop()
    
    def refresh_logs(self):
        """Refresh the log file list and content."""
        current_file = self.current_log_file
        self.load_log_files()
        
        # Try to restore the previously selected file
        if current_file and current_file.exists():
            index = self.file_combo.findText(current_file.name)
            if index >= 0:
                self.file_combo.setCurrentIndex(index)
        
        self.status_bar.setText('Logs refreshed')
    
    def save_log(self):
        """Save the current log view to a file."""
        if not self.current_log_file:
            QMessageBox.warning(self, 'No Log File', 'No log file is currently selected.')
            return
            
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            'Save Log As',
            str(self.current_log_file.with_name(f'{self.current_log_file.stem}_filtered.log')),
            'Log Files (*.log);;All Files (*)'
        )
        
        if file_name:
            try:
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(self.text_edit.toPlainText())
                self.status_bar.setText(f'Log saved to {Path(file_name).name}')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to save log file: {str(e)}')
    
    def clear_log(self):
        """Clear the current log file."""
        if not self.current_log_file:
            return
            
        reply = QMessageBox.question(
            self,
            'Confirm Clear',
            f'Are you sure you want to clear {self.current_log_file.name}?\nThis action cannot be undone.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                with open(self.current_log_file, 'w', encoding='utf-8') as f:
                    f.write('')
                self.load_log_content()
                self.status_bar.setText(f'Cleared {self.current_log_file.name}')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to clear log file: {str(e)}')
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.refresh_timer.stop()
        event.accept()


# For backward compatibility
def show_log(root=None):
    """
    Show the log viewer dialog.
    
    Args:
        root: Parent widget (for compatibility with Tkinter version)
    """
    import sys
    
    # Create QApplication if it doesn't exist
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create and show the log viewer
    log_viewer = LogViewer()
    log_viewer.exec()
    
    # If this was the first QApplication, run the event loop
    if QApplication.instance() is None:
        sys.exit(app.exec())


# For direct execution
if __name__ == '__main__':
    show_log()
