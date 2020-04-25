# galaxy-integration-dosbox
A GOG Galaxy 2.0 integration for Dosbox

## Features:
- Add your DOS games to your Library.
- Owned games are expected to be stored in ZIP files making them easier to manage.
- Specify a folder when enabling the plugin. Multiple folders containing ZIP files can be setup (separated by semicolon ";")
- Only Windows is supported.

## How to Install:

Download the .zip from the GitHub as a ZIP file, and extract the contents into your installed plugins folder.
The default folderis at `%localappdata%\GOG.com\Galaxy\plugins\installed`

2) Configure the plugin by editing the `config.py` file, and providing the desired paths and files.

## How to add games:
Games can be stored in any folder, but need to be compressed as ZIP files.
This makes it easier for managing games in many ways.

The format is as follows:
- ZIP file must be named as the actual game (ie: "Prince of Persia").
- Inside the ZIP file, there must be a folder with the very same name (ie: "\Prince of Persia\") which should contain the game files.
- Inside that fodler there must be a PLAY.BAT, PLAY.EXE or PLAY.COM file, which is the file that will be executed once the ZIP is loaded by the emulator.
- In case where the game needs a CDROM inserted with additional files, a extra folder must be created inside the ZIP file named "CDROM", and the files from the CD should be stored there.

Note:
 - A folder for the "created or modified" files is dynamically created for each game when run. This folder can be deleted at any time, which will reset the game to its original install.

## Known Issues/Caveats/Requirements:
- The plugin will be listed as ATARI JAGUAR in GOG Galaxy... as DOS is not a supported platform at this time.
- DotNet 4.0 is required for the executable "DosZipLaunch.exe"
- Visual Studio 2019 Reditributable might be needed for the "Dosbox.exe"

## Acknowledgements
- This DosBox.exe is heavily modified version of another Dosbox mod done by ykhwong.
It can be located at http://www.ykhwong.x-y.net/
- The GOG Galaxy API and templates were done by GOG.
