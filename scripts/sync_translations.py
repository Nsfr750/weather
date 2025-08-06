#!/usr/bin/env python3
"""
Translation Management System

This script provides tools to manage and synchronize translation files.
It uses it.json as the reference file to ensure all language files
have the same set of keys.
"""
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Path to the translations directory
TRANSLATIONS_DIR = Path(__file__).parent.parent / 'lang' / 'translations'
REFERENCE_LANG = 'it.json'
TARGET_LANGUAGES = [
    'ar.json',  # Arabic
    'de.json',  # German
    'en.json',  # English
    'es.json',  # Spanish
    'fr.json',  # French
    'ja.json',  # Japanese
    'pt.json',  # Portuguese
    'ru.json',  # Russian
    'zh.json',  # Chinese (Simplified)
    'hi.json',  # Hindi
    'ko.json',  # Korean
    'tr.json',  # Turkish
    'nl.json',  # Dutch
    'pl.json',  # Polish
    'he.json'   # Hebrew
]

# Translation status indicators
STATUS_MISSING = "❌"  # Missing translation
STATUS_PARTIAL = "⚠️"  # Partially translated (placeholder or similar to English)
STATUS_COMPLETE = "✅"  # Fully translated

class TranslationManager:
    """Manages translation files and provides analysis tools."""
    
    def __init__(self, reference_file: str = None):
        """Initialize with the reference language file."""
        self.reference_file = reference_file or REFERENCE_LANG
        self.reference_path = TRANSLATIONS_DIR / self.reference_file
        self.reference_data = self._load_json_file(self.reference_path)
        
        if not self.reference_data:
            raise ValueError(f"Could not load reference file: {self.reference_path}")
    
    @staticmethod
    def _load_json_file(file_path: Path) -> Optional[Dict]:
        """Load a JSON file and return its content as a dictionary."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {file_path}: {e}", file=sys.stderr)
            return None
    
    @staticmethod
    def _save_json_file(file_path: Path, data: Dict) -> bool:
        """Save data to a JSON file with proper formatting."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
                f.write('\n')  # Add newline at end of file
            return True
        except Exception as e:
            print(f"Error saving {file_path}: {e}", file=sys.stderr)
            return False
    
    def sync_translations(self) -> Dict[str, int]:
        """Sync all language files with the reference language file."""
        results = {}
        
        for lang_file in TARGET_LANGUAGES:
            if lang_file == self.reference_file:
                continue  # Skip the reference file
                
            lang_path = TRANSLATIONS_DIR / lang_file
            
            # Load existing translations if file exists
            if lang_path.exists():
                translations = self._load_json_file(lang_path)
                if translations is None:
                    print(f"Skipping {lang_file} due to load error")
                    continue
            else:
                print(f"Creating new translation file: {lang_file}")
                translations = {}
            
            # Track changes
            added = 0
            
            # Add missing keys from reference
            for key, value in self.reference_data.items():
                if key not in translations:
                    translations[key] = ""  # Add empty string as placeholder
                    added += 1
            
            # Save updated translations if there were changes
            if added > 0:
                if self._save_json_file(lang_path, translations):
                    results[lang_file] = added
                    print(f"Added {added} missing keys to {lang_file}")
            else:
                print(f"No updates needed for {lang_file}")
                results[lang_file] = 0
        
        return results
    
    def analyze_translations(self) -> Dict[str, Dict]:
        """Analyze all translation files and return a report."""
        report = {
            'reference': {
                'file': str(self.reference_file),
                'key_count': len(self.reference_data),
                'keys': list(self.reference_data.keys())
            },
            'languages': {}
        }
        
        for lang_file in [self.reference_file] + TARGET_LANGUAGES:
            if lang_file == self.reference_file:
                continue
                
            lang_path = TRANSLATIONS_DIR / lang_file
            
            if not lang_path.exists():
                report['languages'][lang_file] = {
                    'status': 'missing',
                    'missing': len(self.reference_data),
                    'total': len(self.reference_data),
                    'completion': 0.0,
                    'missing_keys': list(self.reference_data.keys())
                }
                continue
                
            translations = self._load_json_file(lang_path)
            if translations is None:
                report['languages'][lang_file] = {
                    'status': 'error',
                    'error': 'Failed to load file'
                }
                continue
                
            # Calculate missing translations
            missing = []
            for key in self.reference_data:
                if key not in translations or not translations[key].strip():
                    missing.append(key)
            
            total_keys = len(self.reference_data)
            missing_count = len(missing)
            translated_count = total_keys - missing_count
            completion = (translated_count / total_keys) * 100 if total_keys > 0 else 0
            
            # Determine status
            if missing_count == 0:
                status = STATUS_COMPLETE
            elif translated_count == 0:
                status = STATUS_MISSING
            else:
                status = STATUS_PARTIAL
            
            report['languages'][lang_file] = {
                'status': status,
                'translated': translated_count,
                'missing': missing_count,
                'total': total_keys,
                'completion': round(completion, 1),
                'missing_keys': missing
            }
        
        return report
    
    def generate_report(self, output_file: str = None) -> str:
        """Generate a human-readable report of translation status."""
        analysis = self.analyze_translations()
        
        # Build the report
        report_lines = [
            "=" * 80,
            "TRANSLATION STATUS REPORT",
            "=" * 80,
            f"Reference file: {analysis['reference']['file']} ({analysis['reference']['key_count']} keys)",
            "-" * 80,
            ""
        ]
        
        # Sort languages by completion percentage (descending)
        languages = sorted(
            analysis['languages'].items(),
            key=lambda x: x[1].get('completion', 0),
            reverse=True
        )
        
        # Add language status summary
        report_lines.append("LANGUAGE TRANSLATION STATUS")
        report_lines.append("-" * 80)
        
        for lang_file, data in languages:
            if data.get('error'):
                status_line = f"{lang_file}: ❌ Error - {data['error']}"
            else:
                status = data['status']
                completion = data['completion']
                status_line = (
                    f"{lang_file}: {status} {completion}% "
                    f"({data['translated']}/{data['total']} keys)"
                )
            report_lines.append(status_line)
        
        # Add detailed missing keys
        report_lines.extend([
            "",
            "MISSING TRANSLATIONS",
            "-" * 80
        ])
        
        for lang_file, data in languages:
            if data.get('error') or data['missing'] == 0:
                continue
                
            report_lines.append(f"\n{lang_file} - Missing {data['missing']} keys:")
            for i, key in enumerate(data['missing_keys'][:10], 1):
                report_lines.append(f"  {i}. {key}")
            
            if data['missing'] > 10:
                report_lines.append(f"  ... and {data['missing'] - 10} more")
        
        report_lines.extend([
            "",
            "=" * 80,
            f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 80
        ])
        
        report = '\n'.join(report_lines)
        
        # Save to file if specified
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Report saved to: {output_path.absolute()}")
        
        return report

def main():
    """Main entry point for the translation management script."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage translation files')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Sync command
    sync_parser = subparsers.add_parser('sync', help='Sync all translation files with the reference')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate a translation status report')
    report_parser.add_argument('-o', '--output', help='Output file path for the report')
    
    args = parser.parse_args()
    
    try:
        tm = TranslationManager()
        
        if args.command == 'sync':
            print("Syncing translation files...")
            results = tm.sync_translations()
            print("\nSync complete!")
            
            # Show summary
            print("\nSummary of changes:")
            for lang_file, added in results.items():
                print(f"- {lang_file}: {added} keys added")
            
            # Generate report after sync
            print("\nGenerating translation status report...")
            report = tm.generate_report('translation_report.txt')
            print("\n" + "-" * 40)
            print("TRANSLATION STATUS SUMMARY")
            print("-" * 40)
            for line in report.split('\n'):
                if ':' in line and '%' in line and 'keys' in line:
                    print(line)
            print("-" * 40)
            print("Full report saved to: translation_report.txt")
            
        elif args.command == 'report':
            print("Generating translation status report...")
            report = tm.generate_report(args.output)
            print("\n" + report)
            
        else:
            # Default action: sync and show report
            print("Syncing translation files...")
            tm.sync_translations()
            print("\nGenerating translation status report...")
            report = tm.generate_report('translation_report.txt')
            print("\n" + report)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0

if __name__ == "__main__":
    from datetime import datetime
    sys.exit(main())
