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
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal, QRect
from PyQt6.QtGui import (QTextCursor, QTextCharFormat, QColor, QFont, QTextOption,
                        QFontDatabase, QIcon, QPixmap, QPainter)

class LogViewer(QMainWindow):
    """
    A dialog to view and filter application log files using PyQt6.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Log Viewer")
        self.setMinimumSize(800, 600)
        self.icon_font = None
        self._init_icon_font()
        
        # Initialize variables
        self.current_log_file = None  # Initialize current_log_file to None
        self.current_level = 'ALL'    # Default log level filter
        self.refresh_interval = 15000  # Refresh interval in milliseconds (15 seconds)
        
        # Initialize UI
        self.setup_ui()
        
        # Load logs
        self.load_log_files()
        
        # Start auto-refresh timer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_logs)
        self.refresh_timer.start(self.refresh_interval)
        
    def _init_icon_font(self):
        """Initialize the Material Icons font for the buttons."""
        try:
            # Try to load the font from resources
            font_id = QFontDatabase.addApplicationFont(":/fonts/materialdesignicons-webfont.ttf")
            if font_id == -1:
                # Try to load from system fonts
                font_family = "Material Design Icons"
                if font_family in QFontDatabase.families():
                    self.icon_font = QFont(font_family)
                    self.icon_font.setPointSize(12)
                else:
                    logger.warning("Material Icons font not found. Using default icons.")
                    self.icon_font = None
            else:
                font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
                self.icon_font = QFont(font_family)
                self.icon_font.setPointSize(12)
                
            # Define icon mappings (Unicode points for Material Icons)
            self.icon_map = {
                'refresh': '\U000F0450',    # mdi-refresh
                'clear': '\U000F0156',      # mdi-close-box-outline
                'delete': '\U000F01B4',     # mdi-delete-outline
                'save': '\U000F0193',       # mdi-content-save-outline
                'auto_refresh': '\U000F0450', # mdi-refresh (same as refresh)
                'auto_refresh_off': '\U000F0451' # mdi-refresh-off
            }
            
        except Exception as e:
            logger.warning(f"Error initializing icon font: {e}")
            self.icon_font = None
    
    def _create_icon(self, icon_name, size=16, color=None):
        """Create an icon from the Material Icons font."""
        if not self.icon_font or not hasattr(self, 'icon_map') or icon_name not in self.icon_map:
            return QIcon()
            
        # Set default color based on theme
        if color is None:
            # Check if dark theme is active (you may need to adjust this based on your theme system)
            is_dark = self.palette().window().color().lightness() < 128
            color = QColor("#ffffff" if is_dark else "#000000")
        
        # Create a pixmap to draw the icon
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # Set up the painter
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        
        # Set font and color
        self.icon_font.setPointSize(size - 4)  # Slightly smaller than the pixmap
        painter.setFont(self.icon_font)
        painter.setPen(color)
        
        # Draw the icon centered
        text_rect = QRect(0, 0, size, size)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.icon_map[icon_name])
        painter.end()
        
        return QIcon(pixmap)
    
    def _set_button_icons(self):
        """Set icons for all buttons using Material Icons."""
        if not hasattr(self, 'icon_font') or not self.icon_font:
            return
            
        # Set icons for buttons
        self.refresh_btn.setIcon(self._create_icon('refresh'))
        self.clear_btn.setIcon(self._create_icon('clear'))
        self.delete_btn.setIcon(self._create_icon('delete'))
        self.save_btn.setIcon(self._create_icon('save'))
        
        # Set initial auto-refresh icon
        self._update_auto_refresh_icon(self.auto_refresh_btn.isChecked())
    
    def _update_auto_refresh_icon(self, enabled):
        """Update the auto-refresh button icon based on its state."""
        if hasattr(self, 'auto_refresh_btn') and hasattr(self, 'icon_font') and self.icon_font:
            icon_name = 'auto_refresh' if enabled else 'auto_refresh_off'
            self.auto_refresh_btn.setIcon(self._create_icon(icon_name))
    
    def _tr(self, text):
        """Translation placeholder - returns text as is for English."""
        return text
        
    def translate_ui(self):
        """Translate the UI elements to the current language.
        
        This is a no-op since we're keeping the UI in English only.
        """
        pass
    
    def setup_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('Log Viewer')
        self.setMinimumSize(900, 600)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Set up UI elements with English text
        self.file_label = QLabel("Log File:")
        self.level_label = QLabel("Log Level:")
        
        # Log level combo box will be set up later in the control frame
        
        # Buttons with icons
        self.refresh_btn = QPushButton(" Refresh")
        self.clear_btn = QPushButton(" Clear")
        self.delete_btn = QPushButton(" Delete")
        self.save_btn = QPushButton(" Save As...")
        self.auto_refresh_btn = QPushButton(" Auto-refresh")
        self.auto_refresh_btn.setCheckable(True)
        self.auto_refresh_btn.setChecked(True)
        
        # Set button icons using Material Icons
        self._set_button_icons()
        
        # Set tooltips with keyboard shortcuts
        self.refresh_btn.setToolTip("Refresh log view (F5)")
        self.clear_btn.setToolTip("Clear the log file (Ctrl+L)")
        self.delete_btn.setToolTip("Delete the log file (Del)")
        self.auto_refresh_btn.setToolTip("Toggle auto-refresh of logs (Ctrl+R)")
        self.save_btn.setToolTip("Save the log file (Ctrl+S)")
        
        # Set keyboard shortcuts
        self.refresh_btn.setShortcut("F5")
        self.clear_btn.setShortcut("Ctrl+L")
        self.delete_btn.setShortcut("Delete")
        self.auto_refresh_btn.setShortcut("Ctrl+R")
        self.save_btn.setShortcut("Ctrl+S")
        
        # Connect buttons
        self.refresh_btn.clicked.connect(self.refresh_logs)
        self.clear_btn.clicked.connect(self.clear_logs)
        self.delete_btn.clicked.connect(self.delete_log)
        self.save_btn.clicked.connect(self.save_log_as)
        self.auto_refresh_btn.toggled.connect(self.toggle_auto_refresh)
        # Connect the auto-refresh button's toggled signal to update its icon
        self.auto_refresh_btn.toggled.connect(self._update_auto_refresh_icon)
        
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
        self.level_label = QLabel("Log Level:")
        control_layout.addWidget(self.level_label)
        
        self.level_combo = QComboBox()
        levels = ["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for level in levels:
            self.level_combo.addItem(level, level)
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
        
        # Add Close button at the bottom
        close_btn = QPushButton('Close')
        close_btn.clicked.connect(self.close)
        close_btn.setFixedWidth(100)
        
        # Create a horizontal layout for the close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # Push button to the right
        button_layout.addWidget(close_btn)
        
        # Add the button layout to the main layout
        main_layout.addLayout(button_layout)
        
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
                color: white;
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
        
        # Try to extract log level from the line (case-insensitive)
        level_match = re.search(r'\[([a-zA-Z]+)\]', line)
        if level_match:
            level_str = level_match.group(1).upper()
            if level_str in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
                log_level = level_str
        
        # Skip if log level doesn't match the filter (case-insensitive comparison)
        if (self.current_level != 'ALL' and 
            log_level.upper() != self.current_level.upper()):
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
    def load_log_content(self):
        """Load the content of the selected log file with the current filters."""
        if not self.current_log_file or not self.current_log_file.exists():
            self.log_display.clear()
            return
            
        try:
            with open(self.current_log_file, 'r', encoding='utf-8') as f:
                self.log_display.clear()
                for line in f:
                    self._process_log_line(line.strip())
        except Exception as e:
            self.log_display.clear()
            self.log_display.append(f"Error loading log file: {str(e)}")
    
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
    
    def on_level_select(self, level_text):
        """Handle log level filter selection.
        
        Args:
            level_text: The text of the selected level in the combo box
        """
        if level_text:  # Check if text is not empty
            self.current_level = level_text
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
        # Update the icon based on the new state
        self._update_auto_refresh_icon(checked)
    
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
    
    def clear_logs(self):
        """Clear the currently selected log file."""
        if not self.current_log_file:
            QMessageBox.warning(self, 'No Log File', 'No log file is currently selected.')
            return
            
        # Ask for confirmation
        reply = QMessageBox.question(
            self,
            'Confirm Clear',
            f'Are you sure you want to clear "{self.current_log_file.name}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Clear the file by opening in write mode and closing immediately
                with open(self.current_log_file, 'w', encoding='utf-8') as f:
                    pass
                self.status_bar.showMessage('Log file cleared')
                self.refresh_logs()  # Refresh the display
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to clear log file: {str(e)}')
    
    def delete_log(self):
        """Delete the currently selected log file."""
        if not self.current_log_file:
            QMessageBox.warning(self, 'No Log File', 'No log file is currently selected.')
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
                
                self.status_bar.showMessage('Log file moved to trash')
                
        except Exception as e:
            QMessageBox.critical(
                self,
                'Error',
                f'Failed to delete log file: {str(e)}'
            )
    
    def save_log_as(self):
        """Save the current log content to a new file."""
        if not self.current_log_file:
            QMessageBox.warning(self, 'No Log File', 'No log file is currently selected.')
            return
            
        # Get the default save location
        default_name = f"{self.current_log_file.stem}_saved{self.current_log_file.suffix}"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            'Save Log As',
            str(self.current_log_file.parent / default_name),
            'Log Files (*.log);;Text Files (*.txt);;All Files (*)'
        )
        
        if file_path:
            try:
                # Get the current log content
                log_content = self.log_display.toPlainText()
                
                # Save to the new file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(log_content)
                
                self.status_bar.showMessage(f'Log saved to {Path(file_path).name}')
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    'Error',
                    f'Failed to save log file: {str(e)}'
                )
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.refresh_timer.stop()
        event.accept()


def show_log(parent=None):
    """
    Show the log viewer dialog.
    
    Args:
        parent: Parent widget
    """
    log_viewer = LogViewer(parent)
    log_viewer.show()
    log_viewer.raise_()
    log_viewer.activateWindow()
    return log_viewer

# For direct execution
if __name__ == '__main__':
    app = QApplication([])
    log_viewer = LogViewer()
    log_viewer.show()
    app.exec()
