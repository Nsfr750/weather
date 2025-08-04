import os
import re
from pathlib import Path
from datetime import datetime

try:
    from send2trash import send2trash
except ImportError:
    send2trash = None

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QTextEdit, QFileDialog, QMessageBox, QFrame, QSizePolicy, QApplication,
    QWidget, QStatusBar, QMainWindow
)
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QColor, QFont, QTextOption

# Import language manager
from lang.language_manager import LanguageManager

class LogViewer(QMainWindow):
    """
    A dialog to view and filter application log files using PyQt6.
    """
    
    def __init__(self, parent=None, translations_manager=None, language='en'):
        super().__init__(parent)
        
        # Store references
        self.translations_manager = translations_manager or getattr(parent, 'translations_manager', None)
        self.language = language
        self.current_log_file = None  # Initialize current_log_file to None
        self.current_level = 'ALL'    # Default log level filter
        self.refresh_interval = 5000  # Default refresh interval in milliseconds (5 seconds)
        
        # Initialize UI
        self.setup_ui()
        self.translate_ui()
        
        # Load logs
        self.load_log_files()
        
        # Start auto-refresh timer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_logs)
        self.refresh_timer.start(self.refresh_interval)
        
    def translate_ui(self):
        """Translate the UI elements to the current language."""
        if not self.translations_manager:
            return
            
        # Set window title
        self.setWindowTitle(self._tr("Log Viewer"))
        
        # Set labels
        self.file_label.setText(self._tr("Log File:"))
        self.level_label.setText(self._tr("Log Level:"))
               
        # Set tooltips
        self.refresh_btn.setToolTip(self._tr("Refresh log view"))
        self.clear_btn.setToolTip(self._tr("Clear the log file"))
        self.delete_btn.setToolTip(self._tr("Delete the log file"))
        self.auto_refresh_btn.setToolTip(self._tr("Toggle auto-refresh of logs"))
        self.save_btn.setToolTip(self._tr("Save the log file"))
        
        # Update log level combo box
        current_level = self.level_combo.currentText()
        self.level_combo.clear()
        levels = ["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for level in levels:
            self.level_combo.addItem(self._tr(level), level)
        
        # Restore selected level if possible
        index = self.level_combo.findText(self._tr(current_level))
        if index >= 0:
            self.level_combo.setCurrentIndex(index)
    
    def _tr(self, text):
        """Translate text using the translations manager if available."""
        if self.translations_manager:
            return self.translations_manager.t(text)
        return text
    
    def set_language(self, language):
        """Update the language of the UI."""
        self.language = language
        self.translate_ui()
    
    def setup_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('Log Viewer')
        self.setMinimumSize(900, 600)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Main layout
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Control frame
        control_frame = QFrame()
        control_layout = QHBoxLayout(control_frame)
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.setSpacing(10)
        
        # Log file selection
        self.file_label = QLabel()
        control_layout.addWidget(self.file_label)
        
        self.file_combo = QComboBox()
        self.file_combo.setMinimumWidth(300)
        self.file_combo.currentIndexChanged.connect(self.on_file_select)
        control_layout.addWidget(self.file_combo)
        
        # Log level filter
        self.level_label = QLabel()
        control_layout.addWidget(self.level_label)
        
        self.level_combo = QComboBox()
        self.level_combo.currentTextChanged.connect(self.on_level_select)
        control_layout.addWidget(self.level_combo)
        
        # Refresh button
        self.refresh_btn = QPushButton('🔁')
        self.refresh_btn.setFixedWidth(30)
        self.refresh_btn.clicked.connect(self.refresh_logs)
        control_layout.addWidget(self.refresh_btn)
        
        # Auto-refresh toggle
        self.auto_refresh_btn = QPushButton('🔀')
        self.auto_refresh_btn.setFixedWidth(30)
        self.auto_refresh_btn.setCheckable(True)
        self.auto_refresh_btn.setChecked(True)
        self.auto_refresh_btn.toggled.connect(self.toggle_auto_refresh)
        control_layout.addWidget(self.auto_refresh_btn)
        
        # Add delete log button
        self.delete_btn = QPushButton('🗑️')
        self.delete_btn.setFixedWidth(30)
        self.delete_btn.clicked.connect(self.delete_log_file)
        control_layout.addWidget(self.delete_btn)
        
        # Add save log button
        self.save_btn = QPushButton('💾')
        self.save_btn.setFixedWidth(30)
        self.save_btn.clicked.connect(self.save_log_file)
        control_layout.addWidget(self.save_btn)
        
        # Add clear log button
        self.clear_btn = QPushButton('📖')
        self.clear_btn.setToolTip('Clear log display')
        self.clear_btn.setFixedWidth(30)
        self.clear_btn.clicked.connect(self.clear_log_display)
        control_layout.addWidget(self.clear_btn)
        
        # Add stretch to push controls to the left
        control_layout.addStretch()
        
        # Add control frame to main layout
        main_layout.addWidget(control_frame)
        
        # Log display area
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.log_display.setFont(QFont('Consolas', 9))
        self.log_display.setStyleSheet(''':focus { border: none; }''')
        
        # Set document options to prevent word wrap and enable horizontal scrollbar
        self.log_document = self.log_display.document()
        self.log_document.setDocumentMargin(0)
        option = QTextOption()
        option.setWrapMode(QTextOption.WrapMode.NoWrap)
        self.log_document.setDefaultTextOption(option)
        
        main_layout.addWidget(self.log_display)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Apply initial translations
        self.translate_ui()
    
    def apply_dark_theme(self):
        """Apply a dark theme to the log viewer."""
        self.setStyleSheet("""
            QMainWindow {
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
            log_dir = Path('logs')
            
            # Create logs directory if it doesn't exist
            if not log_dir.exists():
                log_dir.mkdir(parents=True, exist_ok=True)
                self.status_bar.showMessage('Logs directory created. No log files found yet.')
                self.log_display.setPlainText('No log files found. Logs will appear here after they are created.')
                return
                
            log_files = sorted(
                [f for f in log_dir.glob('*.log') if f.is_file()],
                key=os.path.getmtime,
                reverse=True
            )
            
            if not log_files:
                self.status_bar.showMessage('No log files found in logs directory')
                self.log_display.setPlainText('No log files found. Logs will appear here after they are created.')
                return
                
            for log_file in log_files:
                self.file_combo.addItem(log_file.name, log_file)
                
            if log_files:
                self.current_log_file = log_files[0]
                self.load_log_content()
                self.delete_btn.setEnabled(True)
            
        except Exception as e:
            error_msg = f'Error loading log files: {str(e)}'
            self.status_bar.showMessage(error_msg)
            self.log_display.setPlainText(error_msg)
            logger.error(error_msg, exc_info=True)
    
    def load_log_content(self):
        """Load the content of the selected log file with the current filters."""
        if not self.current_log_file or not self.current_log_file.exists():
            self.status_bar.showMessage('Log file not found')
            return
            
        try:
            self.log_display.clear()
            
            with open(self.current_log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    self._process_log_line(line.strip())
                    
            self.status_bar.showMessage(f'Loaded {self.current_log_file.name}')
            
            # Scroll to bottom
            cursor = self.log_display.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.log_display.setTextCursor(cursor)
            
        except Exception as e:
            self.status_bar.showMessage(f'Error loading log file: {str(e)}')
    
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
        cursor = self.log_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        # Apply formatting
        cursor.insertText(line + '\n', format)
    
    def on_file_select(self, index):
        """Handle log file selection."""
        if index >= 0:
            self.current_log_file = self.file_combo.itemData(index)
            if self.current_log_file and self.current_log_file.exists():
                self.load_log_content()
                self.delete_btn.setEnabled(True)
            else:
                self.log_display.clear()
                self.status_bar.showMessage('Selected log file does not exist')
                self.delete_btn.setEnabled(False)
    
    def on_level_select(self, level):
        """Handle log level filter selection."""
        self.current_level = level
        if self.current_log_file and self.current_log_file.exists():
            self.load_log_content()
    
    def toggle_auto_refresh(self, checked):
        """Toggle auto-refresh of logs."""
        if checked:
            self.refresh_timer.start(self.refresh_interval)
            self.refresh_btn.setEnabled(False)
        else:
            self.refresh_timer.stop()
            self.refresh_btn.setEnabled(True)
        self.auto_refresh_btn.setChecked(checked)
    
    def refresh_logs(self):
        """Refresh the log file list and content."""
        current_file = self.current_log_file
        self.load_log_files()
        
        # Try to restore the previously selected file
        if current_file and current_file.exists():
            index = self.file_combo.findText(current_file.name)
            if index >= 0:
                self.file_combo.setCurrentIndex(index)
        
        self.status_bar.showMessage('Logs refreshed')
    
    def save_log_file(self):
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
                    f.write(self.log_display.toPlainText())
                self.status_bar.showMessage(f'Log saved to {Path(file_name).name}')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to save log file: {str(e)}')
    
    def clear_log_display(self):
        """Clear the current log display."""
        self.log_display.clear()
    
    def delete_log_file(self):
        """Delete the currently selected log file using send2trash."""
        if not self.current_log_file:
            return
            
        if send2trash is None:
            QMessageBox.critical(
                self,
                'Error',
                'The send2trash module is not installed.\n'
                'Please install it with: pip install send2trash'
            )
            return
            
        try:
            # Ask for confirmation
            reply = QMessageBox.question(
                self,
                'Confirm Delete',
                f'Are you sure you want to move "{self.current_log_file.name}" to the trash?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Move file to trash
                send2trash(str(self.current_log_file))
                
                # Update UI
                current_index = self.file_combo.currentIndex()
                self.file_combo.removeItem(current_index)
                
                # Select next or previous item
                new_count = self.file_combo.count()
                if new_count > 0:
                    new_index = min(current_index, new_count - 1)
                    self.file_combo.setCurrentIndex(new_index)
                else:
                    self.current_log_file = None
                    self.log_display.clear()
                    self.delete_btn.setEnabled(False)
                
                QMessageBox.information(
                    self,
                    'Success',
                    'The log file has been moved to the trash.'
                )
                
        except Exception as e:
            QMessageBox.critical(
                self,
                'Error',
                f'Failed to delete log file: {str(e)}'
            )
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.refresh_timer.stop()
        event.accept()


def show_log(parent=None, translations_manager=None, language='en'):
    """
    Show the log viewer dialog.
    
    Args:
        parent: Parent widget
        translations_manager: Translations manager instance
        language: Current language code
    """
    if not hasattr(show_log, 'instance') or show_log.instance is None:
        show_log.instance = LogViewer(parent, translations_manager, language)
    
    # Update translations if needed
    if translations_manager is not None:
        show_log.instance.translations_manager = translations_manager
        show_log.instance.set_language(language)
    
    show_log.instance.show()
    show_log.instance.raise_()
    show_log.instance.activateWindow()
    return show_log.instance

# For direct execution
if __name__ == '__main__':
    app = QApplication([])
    log_viewer = LogViewer()
    log_viewer.show()
    app.exec()
