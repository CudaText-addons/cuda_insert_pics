plugin for CudaText.
gives ability to insert picture-files (png/jpeg/gif) into inter-line gaps, pics will show
between lines.

plugin gives commands in the Plugins menu: add pic, delete pic(s).
prompt to resize is shown, if width of pic-file is bigger than eg 500.

when file saves, plugin creates helper file with extent .cuda-notes (in the same dir),
it is JSON file with info about inserted pictures.
pictures are saved in Base64 encoding here. so helper file is big.
on opening file, plugin reads this helper file, and re-adds pictures from it.
it creates pic-files in the temp-folder.

during editing, if you insert/delete lines, pics are glued to their orig lines.
they're deleted only if you delete their lines, or use plugin's commands to delete pics.


license: MIT
author: Alexey (CudaText)
