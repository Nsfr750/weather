import subprocess
import os
import sys
import shutil
import stat
from pathlib import Path

def get_version():
    """Get version information from script/version.py"""
    try:
        sys.path.insert(0, 'script')
        from version import get_version, VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH, VERSION_QUALIFIER
        version_str = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"
        if VERSION_QUALIFIER:
            version_str += f"-{VERSION_QUALIFIER}"
        display_version = get_version()
        return version_str, display_version
    except Exception as e:
        print(f"Warning: Could not read version: {e}")
        return "1.6.0", "1.6.0"

def create_spec_file(version_str, display_version):
    """Create PyInstaller spec file"""
    # Ensure version has 4 elements
    version_parts = list(map(int, version_str.split('.')))
    while len(version_parts) < 4:
        version_parts.append(0)
    version_tuple = tuple(version_parts)
    
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/*', 'assets'),
        ('config/*.json', 'config'),
        ('assets/version_info.txt', 'assets'),
        ('assets/weather_icons/*.png', 'assets/weather_icons'),
        ('lang/*', 'lang'),
        ('lang/translations/*.json', 'lang/translations'),
        ('script/weather_providers', 'script/weather_providers'),
        ('docs/*.md', 'docs'),
    ],
    hiddenimports=[
        'requests',
        'geopy',
        'timezonefinder',
        'pytz',
        'PyQt6',
        'PyQt6.QtNetwork',
        'PyQt6.QtWidgets',
        'script.weather_providers.openmeteo',
    ],
    hookspy=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WeatherApp-{version_str}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=['python3.dll'],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
    version='version.txt',
    uac_admin=False,
)
"""
    # Create version file for Windows
    version_info = """# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers={version_tuple},
    prodvers={version_tuple},
    # Contains a bitmask that specifies the valid bits 'flags'.
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x40004,
    # The general type of file.
    # 0x1 - the file is an application.
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          '040904B0',
          [StringStruct('CompanyName', 'Tuxxle'),
           StringStruct('FileDescription', 'Wheather App.'),
           StringStruct('FileVersion', '{version_str}'),
           StringStruct('InternalName', 'Wheather'),
           StringStruct('LegalCopyright', '© 2025 Nsfr750 - All Rights Reserved'),
           StringStruct('OriginalFilename', 'Wheather-{version_str}.exe'),
           StringStruct('ProductName', 'Wheather'),
           StringStruct('ProductVersion', '{display_version}')])
      ]
    ),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
""".format(version_tuple=version_tuple, 
             version_str=version_str, 
             display_version=display_version)

    with open('version.txt', 'w', encoding='utf-8') as f:
        f.write(version_info)
    
    with open('wheather.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)

def main():
    print("Building Wheather with PyInstaller...")
    
    def remove_readonly(func, path, _):
        """Remove readonly attribute and retry the operation"""
        os.chmod(path, stat.S_IWRITE)
        func(path)

    # Clean previous builds
    build_dir = 'build'
    dist_dir = 'dist'
    
    def remove_readonly_files(func, path, _):
        """Remove readonly attribute and retry the operation"""
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception as e:
            print(f"Warning: Could not remove {path}: {e}")
    
    # Clean build directory
    if os.path.exists(build_dir):
        print("Cleaning build directory...")
        shutil.rmtree(build_dir, onerror=remove_readonly_files, ignore_errors=True)
    
    # Clean dist directory
    if os.path.exists(dist_dir):
        print("Cleaning dist directory...")
        # Try to remove the directory and all its contents
        try:
            shutil.rmtree(dist_dir, onerror=remove_readonly_files, ignore_errors=True)
        except Exception as e:
            print(f"Warning: Could not fully clean dist directory: {e}")
            # If we can't remove the directory, at least try to clean its contents
            for item in os.listdir(dist_dir):
                item_path = os.path.join(dist_dir, item)
                try:
                    if os.path.isfile(item_path):
                        os.chmod(item_path, stat.S_IWRITE)
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path, onerror=remove_readonly_files, ignore_errors=True)
                except Exception as e:
                    print(f"Warning: Could not remove {item_path}: {e}")
    
    # Get version information
    version_str, display_version = get_version()
    print(f"Building version: {display_version} (using build version: {version_str})")
    
    # Create spec file
    print("Creating PyInstaller spec file...")
    create_spec_file(version_str, display_version)
    
    # Build command
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        "wheather.spec"
    ]
    
    # Run the command
    print("Starting build...")
    try:
        subprocess.run(cmd, check=True)
        print("\nBuild completed successfully!")
        print(f"Output directory: {os.path.abspath(dist_dir)}")
        
        # Clean up temporary files
        if os.path.exists('version.txt'):
            os.remove('version.txt')
        if os.path.exists('wheather.spec'):
            os.remove('wheather.spec')
            
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with exit code {e.returncode}")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during build: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
