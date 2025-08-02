"""
Feature Manager

Manages the loading, configuration, and lifecycle of feature plugins.
"""
import importlib
import importlib.util
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Type, Any, TypeVar, Generic

from .plugin_manager import BasePlugin, PluginManager

logger = logging.getLogger(__name__)

# Type variable for feature plugins
T = TypeVar('T', bound='BaseFeature')

class BaseFeature(BasePlugin):
    """Base class for all feature plugins."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.initialized = False
    
    def initialize(self) -> bool:
        """Initialize the feature."""
        self.initialized = True
        return True
    
    def cleanup(self) -> None:
        """Clean up resources used by the feature."""
        self.initialized = False


class FeatureManager(Generic[T]):
    """Manages feature plugins."""
    
    def __init__(self, plugin_manager: PluginManager):
        """Initialize the feature manager."""
        self.plugin_manager = plugin_manager
        self.features: Dict[str, T] = {}
        self._feature_configs: Dict[str, Dict[str, Any]] = {}
        self._load_feature_configs()
    
    def _load_feature_configs(self) -> None:
        """Load feature configurations from the config file."""
        config_path = Path("config") / "features.json"
        if config_path.exists():
            try:
                import json
                with open(config_path, 'r', encoding='utf-8') as f:
                    self._feature_configs = json.load(f)
            except Exception as e:
                logger.error(f"Error loading feature configs: {e}")
    
    def _save_feature_configs(self) -> None:
        """Save feature configurations to the config file."""
        config_path = Path("config")
        config_path.mkdir(exist_ok=True)
        
        try:
            import json
            with open(config_path / "features.json", 'w', encoding='utf-8') as f:
                json.dump(self._feature_configs, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving feature configs: {e}")
    
    def load_features(self, feature_dir: str = "plugins/features") -> None:
        """Load all available features from the specified directory."""
        feature_path = Path(feature_dir)
        if not feature_path.exists():
            logger.warning(f"Feature directory {feature_dir} does not exist")
            return
        
        # Add the parent directory to sys.path to allow relative imports
        parent_dir = str(feature_path.parent.absolute())
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        # Import all Python files in the feature directory
        for file in feature_path.glob("*.py"):
            if file.name.startswith("_"):
                continue
                
            module_name = file.stem
            try:
                # Import the module using the full path
                spec = importlib.util.spec_from_file_location(
                    f"plugins.features.{module_name}", 
                    str(file.absolute())
                )
                if spec is None or spec.loader is None:
                    logger.error(f"Could not load spec from {file}")
                    continue
                
                module = importlib.util.module_from_spec(spec)
                sys.modules[f"plugins.features.{module_name}"] = module
                spec.loader.exec_module(module)
                
                # Find all feature classes in the module
                for name, obj in module.__dict__.items():
                    if (isinstance(obj, type) and 
                        issubclass(obj, BaseFeature) and 
                        obj != BaseFeature):
                        
                        # Get or create config for this feature
                        config = self._feature_configs.get(module_name, {})
                        
                        # Initialize the feature
                        try:
                            feature = obj(**config)
                            if feature.initialize():
                                self.features[module_name] = feature
                                logger.info(f"Loaded feature: {module_name}")
                        except Exception as e:
                            logger.error(f"Error initializing feature {module_name}: {e}")
            
            except ImportError as e:
                logger.error(f"Error importing feature module {module_name}: {e}")
    
    def get_feature(self, name: str) -> Optional[T]:
        """Get a feature by name."""
        return self.features.get(name)
    
    def get_features(self) -> Dict[str, T]:
        """Get all loaded features."""
        return self.features
    
    def is_feature_enabled(self, name: str) -> bool:
        """Check if a feature is enabled."""
        return name in self.features and self.features[name].initialized
    
    def update_feature_config(self, name: str, config: Dict[str, Any]) -> bool:
        """Update a feature's configuration."""
        if name not in self.features:
            return False
        
        try:
            # Update the feature's config
            self.features[name].__dict__.update(config)
            
            # Save the config
            self._feature_configs[name] = config
            self._save_feature_configs()
            
            # Reinitialize the feature
            if not self.features[name].initialize():
                logger.error(f"Failed to reinitialize feature {name} after config update")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error updating feature {name} config: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up all features."""
        for feature in self.features.values():
            try:
                feature.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up feature {feature.__class__.__name__}: {e}")
