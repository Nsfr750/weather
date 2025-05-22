# Changelog

## [1.2.0-beta] - 2025-05-22
### Added
- Help dialog is now fully multi-language (English, Spanish, Italian)
- All help content and tab titles use the modularized translation system
- UI updates instantly when language is changed
- Improved documentation and modularity for translation logic

### Changed
- Version bumped to 1.2.0-beta to reflect major modularization and help dialog improvements

# Changelog

## [1.2.0] - 2025-05-22
### Major Improvements
- Added error logging to `weather_app.log` for easier troubleshooting
- Introduced a built-in log viewer dialog
- Favorites system: save and quickly access favorite cities
- Unit selection: switch between metric (°C, m/s) and imperial (°F, mph)
- Persistent API key storage in `config.json` and via the settings dialog
- Multi-language support: English, Spanish, Italian (UI and weather descriptions)

### UI/UX
- Updated help and settings dialogs to reflect new features
- Enhanced menu bar for improved navigation

---

## [1.1.0-alpha] - 2025-05-22
### Initial Release
- Modern, responsive GUI with Tkinter
- Light/dark theme toggle
- Real-time current weather and 5-day forecast
- Menu bar: About, Help, Sponsor, Settings
- Help dialog with usage, features, and tips
- Settings dialog for API key management

---

## Future Plans
- Weather icons fallback for offline use
- Desktop notifications for severe weather
- Animated transitions for theme switch
- Improved accessibility (keyboard navigation, color contrast)
- More languages and customization options

---
*See previous versions in version.py if available.*

## [1.1.0-alpha] - 2025-05-22
### Added
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
