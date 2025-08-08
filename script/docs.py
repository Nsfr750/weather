#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Documentation Viewer

A modern documentation viewer for JSON documentation files with dark theme support.
"""

import os
import sys
import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextBrowser, QVBoxLayout, QWidget, QPushButton,
    QHBoxLayout, QMessageBox, QStatusBar, QFileDialog, QTreeWidget, QTreeWidgetItem,
    QSplitter
)
from PyQt6.QtCore import Qt, QUrl, QSize
from PyQt6.QtGui import QAction, QFont, QTextCursor, QIcon, QDesktopServices

# Import language manager
from lang.language_manager import get_language_manager

class DocumentationViewer(QMainWindow):
    def __init__(self, language='en'):
        super().__init__()
        self.language = language.lower()
        self.language_manager = get_language_manager()
        self.zoom_level = 0
        self.current_file = None
        
        # Set up documentation paths
        self.docs_dir = Path('script')
        self.json_docs_dir = self.docs_dir / 'documentation'
        
        # Create JSON docs directory if it doesn't exist
        self.json_docs_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize UI
        self.init_ui()
        
        # Load documentation index
        self.load_documentation()
        
        # Load default document
        self.load_default_document()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle(self.language_manager.get('documentation', 'Documentation'))
        self.setGeometry(100, 100, 1000, 700)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create splitter for navigation and content
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel: Navigation tree
        self.nav_tree = QTreeWidget()
        self.nav_tree.setHeaderHidden(True)
        self.nav_tree.setMinimumWidth(250)
        self.nav_tree.setMaximumWidth(400)
        self.nav_tree.itemClicked.connect(self.on_nav_item_clicked)
        
        # Right panel: Content
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Content area
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(False)
        self.text_browser.setReadOnly(True)
        self.text_browser.anchorClicked.connect(self.on_link_clicked)
        self.text_browser.setOpenLinks(False)
        
        # Create toolbar after text_browser is initialized
        self.create_toolbar()
        
        # Add widgets to right panel
        right_layout.addWidget(self.text_browser)
        
        # Add panels to splitter
        self.splitter.addWidget(self.nav_tree)
        self.splitter.addWidget(right_panel)
        
        # Set initial splitter sizes
        self.splitter.setSizes([250, 750])
        
        # Add splitter to main layout
        layout.addWidget(self.splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Apply dark theme
        self.apply_dark_theme()
    
    def create_toolbar(self):
        """Create the application toolbar."""
        toolbar = self.addToolBar('Main Toolbar')
        
        # Back button
        back_action = QAction('Back', self)
        back_action.setShortcut('Alt+Left')
        back_action.triggered.connect(self.text_browser.backward)
        toolbar.addAction(back_action)
        
        # Forward button
        forward_action = QAction('Forward', self)
        forward_action.setShortcut('Alt+Right')
        forward_action.triggered.connect(self.text_browser.forward)
        toolbar.addAction(forward_action)
        
        # Zoom in
        zoom_in_action = QAction('Zoom In', self)
        zoom_in_action.setShortcut('Ctrl+=')
        zoom_in_action.triggered.connect(self.zoom_in)
        toolbar.addAction(zoom_in_action)
        
        # Zoom out
        zoom_out_action = QAction('Zoom Out', self)
        zoom_out_action.setShortcut('Ctrl+-')
        zoom_out_action.triggered.connect(self.zoom_out)
        toolbar.addAction(zoom_out_action)
        
        # Reset zoom
        reset_zoom_action = QAction('Reset Zoom', self)
        reset_zoom_action.triggered.connect(self.reset_zoom)
        toolbar.addAction(reset_zoom_action)
        
        # Add separator
        toolbar.addSeparator()
        
        # About button
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        toolbar.addAction(about_action)
        
        # Close button
        close_action = QAction('Close', self)
        close_action.setShortcut('Ctrl+W')
        close_action.triggered.connect(self.close)
        toolbar.addAction(close_action)
    
    def apply_dark_theme(self):
        """Apply a dark theme to the application."""
        dark_theme = """
        QMainWindow, QWidget {
            background-color: #2d2d2d;
            color: #e0e0e0;
        }
        QTextBrowser {
            background-color: #1e1e1e;
            color: #e0e0e0;
            border: 1px solid #3e3e3e;
            border-radius: 4px;
            padding: 10px;
        }
        QTreeView {
            background-color: #252526;
            color: #e0e0e0;
            border: 1px solid #3e3e3e;
            border-radius: 4px;
        }
        QTreeView::item {
            padding: 5px;
        }
        QTreeView::item:selected {
            background-color: #37373d;
            color: #ffffff;
        }
        QTreeView::item:hover {
            background-color: #2a2d2e;
        }
        QToolBar {
            background-color: #333333;
            border: none;
            spacing: 3px;
        }
        QToolButton {
            background-color: transparent;
            color: #e0e0e0;
            border: 1px solid transparent;
            border-radius: 4px;
            padding: 3px 8px;
        }
        QToolButton:hover {
            background-color: #3c3c3c;
            border: 1px solid #5d5d5d;
        }
        QToolButton:pressed {
            background-color: #4d4d4d;
        }
        QStatusBar {
            background-color: #0078d7;
            color: white;
        }
        a {
            color: #4da6ff;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #4da6ff;
            margin-top: 1.2em;
            margin-bottom: 0.6em;
        }
        code {
            background-color: #1e1e1e;
            color: #d4d4d4;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', monospace;
        }
        pre {
            background-color: #1e1e1e;
            color: #d4d4d4;
            padding: 10px;
            border-radius: 4px;
            border: 1px solid #3e3e3e;
            overflow-x: auto;
        }
        blockquote {
            border-left: 3px solid #4da6ff;
            margin: 1em 0;
            padding: 0.5em 1em;
            background-color: #2a2d2e;
            color: #b8b8b8;
        }
        """
        
        self.setStyleSheet(dark_theme)
        
        # Set default font
        font = QFont()
        font.setPointSize(10)
        self.setFont(font)
    
    def load_documentation(self):
        """Load the documentation structure into the navigation tree."""
        self.nav_tree.clear()
        
        # Add root item for documentation
        root_item = QTreeWidgetItem(self.nav_tree, [self.language_manager.get('documentation', 'Documentation')])
        root_item.setData(0, Qt.ItemDataRole.UserRole, None)
        
        # Load all JSON files from the documentation directory
        if self.json_docs_dir.exists():
            for json_file in sorted(self.json_docs_dir.glob('*.json')):
                if json_file.name != 'index.json':  # Skip index file
                    # Use the filename without extension as the title
                    title = json_file.stem.replace('_', ' ').title()
                    doc_item = QTreeWidgetItem(root_item, [title])
                    doc_item.setData(0, Qt.ItemDataRole.UserRole, str(json_file))
        
        # Expand the root item
        root_item.setExpanded(True)
    
    def load_default_document(self):
        """Load the default document (index.json)."""
        index_file = self.json_docs_dir / 'index.json'
        if index_file.exists():
            self.load_file(str(index_file))
    
    def load_file(self, file_path):
        """Load and display a documentation file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                doc_data = json.load(f)
            
            # Check if this is the index file with documents list
            if os.path.basename(file_path) == 'index.json' and 'documents' in doc_data:
                # Create a special HTML for the index
                html = self._generate_index_html(doc_data)
                self.text_browser.setHtml(html)
                title = self.language_manager.get('documentation_index', 'Documentation Index')
            else:
                # Build HTML content for regular documentation files
                html = self.generate_html(doc_data)
                self.text_browser.setHtml(html)
                title = doc_data.get('title', os.path.basename(file_path))
            
            # Update window title
            self.setWindowTitle(f"{self.language_manager.get('documentation', 'Documentation')} - {title}")
            
            # Update status bar
            self.status_bar.showMessage(f"Loaded: {os.path.basename(file_path)}")
            
            # Store current file
            self.current_file = file_path
            
            return True
            
        except Exception as e:
            QMessageBox.critical(
                self,
                self.language_manager.get('error', 'Error'),
                f"{self.language_manager.get('error_loading_file', 'Error loading file:')} {str(e)}"
            )
            return False
            
    def _generate_index_html(self, doc_data):
        """Generate HTML for the index page."""
        title = self.language_manager.get('documentation_index', 'Documentation Index')
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{title}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 20px;
                    color: #e0e0e0;
                }}
                h1 {{
                    color: #4da6ff;
                    margin-top: 0;
                    padding-bottom: 10px;
                    border-bottom: 1px solid #3e3e3e;
                }}
                .document-list {{
                    list-style-type: none;
                    padding: 0;
                }}
                .document-item {{
                    margin: 10px 0;
                    padding: 10px;
                    border-left: 3px solid #4da6ff;
                    background-color: #252526;
                    transition: background-color 0.2s;
                }}
                .document-item:hover {{
                    background-color: #2a2d2e;
                }}
                .document-link {{
                    color: #4da6ff;
                    text-decoration: none;
                    font-size: 1.1em;
                    display: block;
                }}
                .document-link:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            <p>{self.language_manager.get('select_document', 'Select a document to view:')}</p>
            <ul class="document-list">
        """
        
        # Add each document as a clickable link
        for doc in doc_data.get('documents', []):
            doc_title = doc.get('title', 'Untitled')
            doc_file = doc.get('filename', '')
            if doc_file:
                html += f"""
                <li class="document-item">
                    <a href="{doc_file}" class="document-link">{doc_title}</a>
                </li>
                """
        
        html += """
            </ul>
        </body>
        </html>
        """
        return html
    
    def _format_content(self, content):
        """Format content with proper HTML tags for line breaks and paragraphs."""
        if not content:
            return ''
            
        # Replace double newlines with paragraphs
        formatted = content.replace('\n\n', '</p><p>')
        # Replace single newlines with line breaks
        formatted = formatted.replace('\n', '<br>')
        # Wrap in paragraph tags if not empty
        if not formatted.startswith('<p>'):
            formatted = f'<p>{formatted}</p>'
        return formatted
        
    def _parse_markdown_table(self, markdown):
        """Parse markdown table into HTML table."""
        if not markdown or not isinstance(markdown, str):
            return markdown
            
        lines = [line.strip() for line in markdown.split('\n') if line.strip()]
        if not lines or len(lines) < 2:
            return markdown
            
        # Check if this is a markdown table (contains | and -)
        if '|' not in lines[0] or '|' not in lines[1] or '--' not in lines[1]:
            return markdown
            
        # Parse headers
        headers = [h.strip() for h in lines[0].split('|') if h.strip()]
        alignments = ['left'] * len(headers)
        
        # Parse alignment from separator line (second line)
        if len(lines) > 1 and '|' in lines[1]:
            aligns = lines[1].split('|')
            for i, align in enumerate(aligns):
                align = align.strip()
                if align.startswith(':') and align.endswith(':'):
                    alignments[i] = 'center'
                elif align.startswith(':'):
                    alignments[i] = 'left'
                elif align.endswith(':'):
                    alignments[i] = 'right'
        
        # Build HTML table
        html = [
            '<div class="table-container" style="overflow-x: auto; margin: 1.5em 0;">',
            '  <table style="border-collapse: collapse; width: 100%; border: 1px solid #3e3e3e;">',
            '    <thead>',
            '      <tr style="background-color: #2a2d2e;">'
        ]
        
        # Add headers
        for i, header in enumerate(headers):
            align = f'text-align: {alignments[i]};' if i < len(alignments) else ''
            html.append(f'        <th style="padding: 10px 12px; border: 1px solid #3e3e3e; {align} font-weight: 600;">{header}</th>')
        
        html.extend([
            '      </tr>',
            '    </thead>',
            '    <tbody>'
        ])
        
        # Add rows (skip first two lines: headers and separator)
        for line in lines[2:]:
            if '|' not in line:
                continue
                
            cells = [cell.strip() for cell in line.split('|') if cell.strip()]
            if len(cells) != len(headers):
                continue
                
            html.append('      <tr style="background-color: #252526;">')
            
            for i, cell in enumerate(cells):
                align = f'text-align: {alignments[i]};' if i < len(alignments) else ''
                html.append(f'        <td style="padding: 8px 12px; border: 1px solid #3e3e3e; {align} vertical-align: top; line-height: 1.5;">{cell}</td>')
            
            html.append('      </tr>')
        
        # Close table
        html.extend([
            '    </tbody>',
            '  </table>',
            '</div>'
        ])
        
        return '\n'.join(html)
    
    def _format_table(self, table_data):
        """Format table data as HTML table."""
        # If we get a string, try to parse it as markdown table
        if isinstance(table_data, str):
            return self._parse_markdown_table(table_data)
            
        if not table_data or not isinstance(table_data, list) or not table_data[0]:
            return ''
            
        # If first row is a list of strings, it's a simple table
        if all(isinstance(cell, str) for cell in table_data[0]):
            headers = table_data[0]
            rows = table_data[1:]
            
            html = [
                '<div class="table-container" style="overflow-x: auto; margin: 1.5em 0;">',
                '  <table style="border-collapse: collapse; width: 100%; border: 1px solid #3e3e3e;">',
                '    <thead>',
                '      <tr style="background-color: #2a2d2e;">'
            ]
            
            # Add headers
            for header in headers:
                html.append(f'        <th style="padding: 10px 12px; border: 1px solid #3e3e3e; text-align: left; font-weight: 600;">{header}</th>')
            
            html.extend([
                '      </tr>',
                '    </thead>',
                '    <tbody>'
            ])
            
            # Add rows
            for row in rows:
                html.append('      <tr style="background-color: #252526;">')
                for cell in row:
                    html.append(f'        <td style="padding: 8px 12px; border: 1px solid #3e3e3e; vertical-align: top; line-height: 1.5;">{cell}</td>')
                html.append('      </tr>')
            
            # Close table
            html.extend([
                '    </tbody>',
                '  </table>',
                '</div>'
            ])
            
            return '\n'.join(html)
            
        # Handle list of dictionaries (complex table structure)
        if all(isinstance(row, dict) for row in table_data):
            # Extract headers from first row keys
            if not table_data:
                return ''
                
            headers = list(table_data[0].keys())
            
            html = [
                '<div class="table-container" style="overflow-x: auto; margin: 1.5em 0;">',
                '  <table style="border-collapse: collapse; width: 100%; border: 1px solid #3e3e3e;">',
                '    <thead>',
                '      <tr style="background-color: #2a2d2e;">'
            ]
            
            # Add headers
            for header in headers:
                html.append(f'        <th style="padding: 10px 12px; border: 1px solid #3e3e3e; text-align: left; font-weight: 600;">{header}</th>')
            
            html.extend([
                '      </tr>',
                '    </thead>',
                '    <tbody>'
            ])
            
            # Add rows
            for row in table_data:
                html.append('      <tr style="background-color: #252526;">')
                for header in headers:
                    cell = row.get(header, '')
                    if isinstance(cell, (list, dict)):
                        cell = str(cell)
                    html.append(f'        <td style="padding: 8px 12px; border: 1px solid #3e3e3e; vertical-align: top; line-height: 1.5;">{cell}</td>')
                html.append('      </tr>')
            
            # Close table
            html.extend([
                '    </tbody>',
                '  </table>',
                '</div>'
            ])
            
            return '\n'.join(html)
            
        # Handle list of lists (simple table structure)
        if all(isinstance(row, list) for row in table_data):
            # Check if first row is a header
            has_header = any(isinstance(cell, dict) and cell.get('header') for cell in table_data[0])
            
            html = [
                '<div class="table-container" style="overflow-x: auto; margin: 1.5em 0;">',
                '  <table style="border-collapse: collapse; width: 100%; border: 1px solid #3e3e3e;">'
            ]
            
            if has_header:
                html.extend([
                    '    <thead>',
                    '      <tr style="background-color: #2a2d2e;">'
                ])
                
                # Add header row
                for cell in table_data[0]:
                    cell_text = cell.get('text', '') if isinstance(cell, dict) else str(cell)
                    align = f'text-align: {cell.get("align", "left")};' if isinstance(cell, dict) and 'align' in cell else ''
                    html.append(f'        <th style="padding: 10px 12px; border: 1px solid #3e3e3e; {align} font-weight: 600;">{cell_text}</th>')
                
                html.extend([
                    '      </tr>',
                    '    </thead>',
                    '    <tbody>'
                ])
                
                # Start from index 1 if we had a header
                rows = table_data[1:] if len(table_data) > 1 else []
            else:
                rows = table_data
                html.append('    <tbody>')
            
            # Add data rows
            for row in rows:
                html.append('      <tr style="background-color: #252526;">')
                
                for cell in row:
                    cell_text = cell.get('text', '') if isinstance(cell, dict) else str(cell)
                    align = f'text-align: {cell.get("align", "left")};' if isinstance(cell, dict) and 'align' in cell else ''
                    html.append(f'        <td style="padding: 8px 12px; border: 1px solid #3e3e3e; {align} vertical-align: top; line-height: 1.5;">{cell_text}</td>')
                
                html.append('      </tr>')
            
            # Close table
            html.extend([
                '    </tbody>',
                '  </table>',
                '</div>'
            ])
            
            return '\n'.join(html)
        
        return ''
    
    def _process_content(self, content):
        """Process content and handle special elements like tables."""
        if isinstance(content, dict):
            if 'type' in content and content['type'] == 'table':
                return self._format_table(content.get('data', []))
            return str(content)
        elif isinstance(content, list):
            # If it's a list of items, create an unordered list
            items = ''.join(f'<li>{self._process_content(item)}</li>' for item in content)
            return f'<ul style="margin: 0.5em 0 0.5em 1.5em; padding: 0;">{items}</ul>'
        return self._format_content(str(content))
    
    def generate_html(self, doc_data):
        """Generate HTML content from documentation data."""
        title = doc_data.get('title', 'Documentation')
        content = doc_data.get('content', '')
        sections = doc_data.get('sections', [])
        
        # Start building HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{title}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 20px;
                    color: #e0e0e0;
                }}
                h1, h2, h3, h4, h5, h6 {{
                    color: #4da6ff;
                    margin-top: 1.2em;
                    margin-bottom: 0.6em;
                }}
                a {{
                    color: #4da6ff;
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
                code {{
                    background-color: #1e1e1e;
                    color: #d4d4d4;
                    padding: 2px 4px;
                    border-radius: 3px;
                    font-family: 'Consolas', 'Monaco', monospace;
                    font-size: 0.95em;
                }}
                pre {{
                    background-color: #1e1e1e;
                    color: #d4d4d4;
                    padding: 12px;
                    border-radius: 4px;
                    border: 1px solid #3e3e3e;
                    overflow-x: auto;
                    line-height: 1.4;
                    margin: 1em 0;
                }}
                pre code {{
                    padding: 0;
                    background: none;
                    border-radius: 0;
                }}
                blockquote {{
                    border-left: 3px solid #4da6ff;
                    margin: 1em 0;
                    padding: 0.5em 1em;
                    background-color: #2a2d2e;
                    color: #b8b8b8;
                    font-style: italic;
                }}
                .section {{
                    margin-bottom: 2em;
                }}
                .section-title {{
                    font-size: 1.5em;
                    color: #4da6ff;
                    margin: 1.5em 0 0.8em 0;
                    padding-bottom: 0.3em;
                    border-bottom: 1px solid #3e3e3e;
                }}
                .section-content {{
                    margin: 0.5em 0 1.5em 1em;
                    line-height: 1.7;
                }}
                .section-content p {{
                    margin: 0.8em 0;
                }}
                .section-content ul, .section-content ol {{
                    margin: 0.8em 0 0.8em 1.5em;
                    padding: 0;
                }}
                .section-content li {{
                    margin-bottom: 0.5em;
                }}
                .note, .warning, .tip, .important {{
                    padding: 12px 15px;
                    margin: 1em 0;
                    border-radius: 4px;
                    border-left: 4px solid #4da6ff;
                    background-color: #2a2d2e;
                }}
                .warning {{
                    border-left-color: #ffcc00;
                    background-color: #332a00;
                }}
                .important {{
                    border-left-color: #ff4d4d;
                    background-color: #330000;
                }}
                .tip {{
                    border-left-color: #4caf50;
                    background-color: #0a2e0c;
                }}
                .admonition-title {{
                    font-weight: bold;
                    margin-top: 0;
                    margin-bottom: 0.5em;
                }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            <div class="section-content">{self._process_content(content)}</div>
        """
        
        # Add sections
        for section in sections:
            section_title = section.get('title', '')
            section_content = section.get('content', '')
            
            html += f"""
            <div class="section">
                <h2 class="section-title">{section_title}</h2>
                <div class="section-content">{self._process_content(section_content)}</div>
            </div>
            """
        
        # Close HTML
        html += """
        </body>
        </html>
        """
        
        return html
    
    def on_nav_item_clicked(self, item):
        """Handle navigation item click."""
        file_path = item.data(0, Qt.ItemDataRole.UserRole)
        if file_path:
            self.load_file(file_path)
    
    def on_link_clicked(self, url):
        """Handle link clicks in the documentation."""
        if url.isRelative() or url.scheme() == 'file':
            # Handle internal links
            if url.scheme() == 'file':
                file_path = url.toLocalFile()
                if os.path.exists(file_path):
                    self.load_file(file_path)
                    return
            
            # Handle anchor links
            anchor = url.fragment()
            if anchor:
                self.text_browser.scrollToAnchor(anchor)
        else:
            # Open external links in default browser
            QDesktopServices.openUrl(url)
    
    def zoom_in(self):
        """Increase the font size."""
        self.zoom_level = min(10, self.zoom_level + 1)
        self.update_font_size()
    
    def zoom_out(self):
        """Decrease the font size."""
        self.zoom_level = max(-5, self.zoom_level - 1)
        self.update_font_size()
    
    def reset_zoom(self):
        """Reset the font size to default."""
        self.zoom_level = 0
        self.update_font_size()
    
    def update_font_size(self):
        """Update the font size based on the current zoom level."""
        font = self.text_browser.font()
        base_size = 10  # Default font size
        font.setPointSize(base_size + self.zoom_level)
        self.text_browser.setFont(font)
    
    def show_about(self):
        """Show the about dialog."""
        about_text = f"""
        <h2>Documentation Viewer</h2>
        <p>Version 1.0.0</p>
        <p>A modern documentation viewer for JSON documentation files.</p>
        <p>© 2023-2025 Nsfr750. All rights reserved.</p>
        <p><a href="https://github.com/Nsfr750/weather">GitHub Repository</a></p>
        """
        
        QMessageBox.about(self, self.language_manager.get('about', 'About'), about_text)
    
    def closeEvent(self, event):
        """Handle window close event."""
        event.accept()


def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Get language from command line or use default
    language = 'EN'  # Default language
    if len(sys.argv) > 1:
        language = sys.argv[1].upper()
    
    # Create and show the main window
    viewer = DocumentationViewer(language=language)
    viewer.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
