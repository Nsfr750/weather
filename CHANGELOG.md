# Changelog

## [Unreleased]

## [1.6.1] - 2025-12-04

### Added
- Added minimize to system tray functionality
  - New option in settings to toggle minimize behavior
  - System tray icon with quick access menu
  - Background updates when minimized
  - Support for all 16 languages

### Fixed
- Fixed translation issues in multiple language files
- Improved system tray icon visibility
- Fixed potential memory leaks in tray icon handling

### Changed
- Updated translations for all supported languages
- Improved error handling for system tray operations
- Enhanced documentation for new features

## [1.6.0] - 2025-08-03

### Added

- New language management system with JSON-based translations
  - Support for 16 languages including:
    - Arabic
    - German
    - English
    - French
    - Hebrew
    - Hungarian
    - Italian
    - Japanese
    - Korean
    - Dutch
    - Polish
    - Portuguese
    - Russian
    - Spanish
    - Turkish
    - Chinese
  - Dynamic language switching without app restart
  - Improved RTL language support
  - Fallback to English for missing translations
- Added comprehensive translation documentation
- Enhanced notification system with system tray integration
  - Support for different alert types (info, warning, error, critical)
  - Persistent notification history
  - Mute notifications option
  - Automatic cleanup of expired alerts
- Weather alerts for severe conditions
  - Heavy precipitation warnings
  - High wind alerts
  - Extreme temperature warnings
  - Nighttime travel advisories
- 7-day forecast support with detailed weather information
- Markdown documentation viewer for help and documentation
- Log viewer for application diagnostics
- Enhanced history entries with additional weather metrics
  - Feels like temperature
  - Humidity percentage
  - Wind speed
  - Atmospheric pressure
  - Visibility data

### Changed

- Refactored translation system from Python dictionaries to JSON files
- Improved error handling for missing translations
- Updated all UI components to use the new translation system
- Optimized translation loading performance

### Fixed
- Map base layer switching in the weather radar dialog
  - Fixed satellite map overlay not displaying correctly
  - Added proper support for OpenTopoMap base layer
  - Fixed Stamen Terrain map layer with proper tile provider
  - Improved layer control and attribution display
- Resolved issues with map rendering and layer management
- Fixed map zoom and pan behavior when switching between different map types
- Fixed issues with special characters in translations
- Resolved RTL text alignment in weather cards
- Fixed translation caching issues

## [1.5.0] - 2025-08-02

### Added

- Multi-language support for error messages and UI elements
- Enhanced logging system with file rotation

### Changed

- Improved error handling and recovery
- Optimized API request batching
- Enhanced weather data caching mechanism
- Updated dependencies to their latest versions
- Improved memory management

### Fixed

- Fixed timezone handling issues
- Resolved race conditions in weather data updates
- Fixed display issues in high-DPI environments
- Addressed memory leaks in weather map rendering
- Fixed translation loading for non-ASCII characters

## [1.4.0] - 2025-07-30

### Added

- Comprehensive documentation in the `/docs` directory, including:
  - User guide with detailed instructions
  - Developer documentation with code style guidelines
  - API documentation for weather providers
  - Troubleshooting guide with common issues and solutions
- Improved error handling and user feedback
- Enhanced logging system with better debugging capabilities
- Automated testing framework with pytest
- Pre-commit hooks for code quality checks

### Changed

- Updated minimum Python version requirement to 3.10+
- Refactored codebase for better maintainability
- Improved performance and reduced memory usage
- Enhanced security for API key management
- Better handling of network connectivity issues

### Fixed

- Fixed issues with language switching
- Resolved threading problems in the update checker
- Addressed various UI glitches and performance bottlenecks
- Fixed compatibility issues with different operating systems
- Resolved caching issues with weather data

## [1.3.0] - 2025-07-30

### Added

- Comprehensive documentation in the `/docs` directory
- New translation strings for all supported languages
- Improved error handling for API responses
- Better logging and debugging capabilities

### Fixed

- Threading and UI update issues in the update checker
- Weather icon attribute mismatch in the main UI
- Datetime import bug in main.py
- Font handling in `_update_metric`
- Language switching and config saving issues
- Various bug fixes and performance improvements

## [1.2.1] - 2025-06-23

### Added

- Automatic update checking on startup
- Manual update check option in Help menu
- Settings dialog for API key management
- Show/hide toggle for API key in settings
- Persistent settings for theme, language, and units
- Better error handling and user feedback

### Fixed

- Menu bar no longer disappears when changing language
- Improved settings dialog layout and usability
- Better error messages for API key validation

## [1.2.0] - 2025-05-22

### Added

- Help dialog is now fully multi-language (English, Spanish, Italian)
- All help content and tab titles use the modularized translation system
- UI updates instantly when language is changed
- Improved documentation and modularity for translation logic

### Changed

- Version bumped to 1.2.0 to reflect major modularization and help dialog improvements
- Added error logging to `weather_app.log` for easier troubleshooting
- Introduced a built-in log viewer dialog
- Favorites system: save and quickly access favorite cities
- Unit selection: switch between metric (°C, m/s) and imperial (°F, mph)
- Persistent API key storage in `config.json` and via the settings dialog
- Multi-language support: English, Spanish, Italian (UI and weather descriptions)

### UI/UX

- Updated help and settings dialogs to reflect new features
- Enhanced menu bar for improved navigation

## [1.1.0] - 2025-05-21

### Initial Release

- Modern, responsive GUI with Tkinter
- Light/dark theme toggle
- Real-time current weather and 5-day forecast
- Menu bar: About, Help, Sponsor, Settings
- Help dialog with usage, features, and tips
- Settings dialog for API key management

## Future Plans

- Weather icons fallback for offline use
- Desktop notifications for severe weather
- Animated transitions for theme switch
- Improved accessibility (keyboard navigation, color contrast)
- More languages and customization options

---
*See previous versions in version.py if available.*

## [1.1.0-alpha] - 2025-05-20

### Initial Features (Alpha)

- Modern, responsive GUI with Tkinter
- Light and dark theme toggle
- Real-time current weather (temperature, humidity, wind speed, icon)
- 5-day forecast with daily details
- Menu bar: About, Help, Sponsor, Settings
- Help dialog with usage, features, and tips
- Settings dialog for API key management

### Changed

- Updated help instructions to match current UI/features

### Removed

- Removed references to map/location and favorites in help
