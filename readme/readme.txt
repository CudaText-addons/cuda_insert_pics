Plugin for CudaText.
Gives the ability to insert picture files (PNG/JPEG/GIF/BMP/ICO) to inter-line gaps,
so pictures will be shown between lines. This works for any file and any syntax
(with plain-text too).

Plugin gives commands in "Plugins / Insert Pics" menu:
- Insert pic
- Remove pic for current line
- Remove all pics

Prompt to resize is shown, if width of picture is bigger than ~500 px.
Picture is auto-resized, if height is bigger than ~500 px.

When file with picture(s) is saved, plugin creates helper file with extention .cuda-pic,
in the same folder. It is JSON file with info about inserted pictures.
Pictures are saved in the helper file, in Base64 encoding, so helper file is big.
On opening original file later, plugin reads the helper file, and re-adds pictures from it.
It creates picture files in the OS temp folder.

During editing, if you insert/delete lines, pics are glued to their original lines.
They're deleted only if you delete their lines, or use plugin's commands to delete pics.


Author: Alexey Torgashin (CudaText)
License: MIT
