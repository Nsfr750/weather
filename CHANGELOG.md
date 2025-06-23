# Changelog

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
