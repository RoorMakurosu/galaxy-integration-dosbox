# galaxy-integration-dosbox
A GOG Galaxy 2.0 integration for Dosbox

Games can be stored in any folder, but need to be compressed as ZIP files.
This makes it easier for managing games in many ways.

The format is as follows:
- ZIP file must be named as the actual game (ie: "Prince of Persia").
- Inside the ZIP file, there must be a folder with the very same name (ie: "\Prince of Persia\") which should contain the game files.
- Inside that fodler there must be a PLAY.BAT, PLAY.EXE or PLAY.COM file, which is the file that will be executed once the ZIP is loaded by the emulator.
- In case where the game needs a CDROM inserted with additional files, a extra folder must be created inside the ZIP file named "CDROM", and the files from the CD should be stored there.

Requirements:
- DotNet 4.0 is required for the executable "DosZipLaunch.exe"
- Visual Studio 2019 Reditributable might be needed for the "Dosbox.exe"

This DosBox.exe is heavily modified version of another Dosbox mod done by ykhwong.
It can be located at http://www.ykhwong.x-y.net/

