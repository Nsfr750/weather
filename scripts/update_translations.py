#!/usr/bin/env python3
"""
Update Translations Script

A streamlined script for managing translations in the Weather application.
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List, Set

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Constants
TRANSLATIONS_DIR = Path(__file__).parent.parent / 'lang' / 'translations'
DEFAULT_REFERENCE = 'it.json'

class TranslationManager:
    """Manages translation files and operations."""
    
    def __init__(self, reference: str = None):
        self.reference = reference or DEFAULT_REFERENCE
        self.translations_dir = TRANSLATIONS_DIR
        self.ref_data = self._load_json(self.translations_dir / self.reference)
        self.languages = self._discover_languages()
    
    def _discover_languages(self) -> List[str]:
        """Find all available language files."""
        return [f.stem for f in self.translations_dir.glob('*.json') 
                if f.is_file() and f.name != self.reference]
    
    def _load_json(self, path: Path) -> dict:
        """Load JSON file with error handling."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {path}: {e}")
            return {}
    
    def _save_json(self, path: Path, data: dict) -> bool:
        """Save data to JSON file."""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
                f.write('\n')
            return True
        except Exception as e:
            logger.error(f"Error saving {path}: {e}")
            return False
    
    def sync(self) -> Dict[str, int]:
        """Sync all language files with reference."""
        results = {}
        ref_keys = set(self.ref_data.keys())
        
        for lang in self.languages:
            path = self.translations_dir / f"{lang}.json"
            data = self._load_json(path)
            missing = ref_keys - set(data.keys())
            
            for key in missing:
                data[key] = ""
            
            if self._save_json(path, data):
                results[lang] = len(missing)
                logger.info(f"Added {len(missing)} keys to {lang}")
            
        return results
    
    def fill(self, source: str = 'en') -> Dict[str, int]:
        """Fill missing translations from source language."""
        source_path = self.translations_dir / f"{source}.json"
        if not source_path.exists():
            logger.error(f"Source language not found: {source}")
            return {}
            
        source_data = self._load_json(source_path)
        results = {}
        
        for lang in self.languages:
            if lang == source:
                continue
                
            path = self.translations_dir / f"{lang}.json"
            data = self._load_json(path)
            filled = 0
            
            for key, value in source_data.items():
                if key in self.ref_data and not data.get(key) and value:
                    data[key] = value
                    filled += 1
            
            if filled and self._save_json(path, data):
                results[lang] = filled
                logger.info(f"Filled {filled} translations in {lang} from {source}")
        
        return results
    
    def report(self) -> str:
        """Generate translation status report."""
        ref_keys = set(self.ref_data.keys())
        report = ["TRANSLATION STATUS REPORT", "=" * 40]
        
        for lang in sorted([self.reference] + self.languages):
            if lang == self.reference:
                continue
                
            path = self.translations_dir / f"{lang}.json"
            data = self._load_json(path)
            
            missing = ref_keys - set(data.keys())
            empty = {k for k, v in data.items() if not v and k in ref_keys}
            total = len(missing) + len(empty)
            percent = ((len(ref_keys) - total) / len(ref_keys)) * 100
            
            status = "✅" if percent == 100 else "⚠️" if percent > 50 else "❌"
            report.append(f"{lang}: {status} {percent:.1f}% ({len(ref_keys) - total}/{len(ref_keys)})")
        
        return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description='Update translations for Weather app')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Sync command
    sync_parser = subparsers.add_parser('sync', help='Sync all language files with reference')
    
    # Fill command
    fill_parser = subparsers.add_parser('fill', help='Fill missing translations from source language')
    fill_parser.add_argument('-s', '--source', default='en', help='Source language (default: en)')
    
    # Report command
    subparsers.add_parser('report', help='Generate translation status report')
    
    # Common arguments
    for p in [parser, sync_parser, fill_parser]:
        p.add_argument('-r', '--reference', default=DEFAULT_REFERENCE,
                     help=f'Reference language file (default: {DEFAULT_REFERENCE})')
    
    args = parser.parse_args()
    
    if not hasattr(args, 'command'):
        parser.print_help()
        return
    
    try:
        manager = TranslationManager(reference=args.reference)
        
        if args.command == 'sync':
            results = manager.sync()
            logger.info(f"\nSynced {len(results)} language files")
            
        elif args.command == 'fill':
            results = manager.fill(source=args.source)
            logger.info(f"\nFilled translations in {len(results)} language files")
            
        elif args.command == 'report':
            print(manager.report())
            
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
