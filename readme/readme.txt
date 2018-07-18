plugin for CudaText.
gives ability to insert picture files (png/jpeg/gif/bmp/ico) into inter-line gaps, 
ie, pics will show between lines.

plugin gives commands in the Plugins menu: add pic, delete pic(s).
prompt to resize is shown, if width of pic is bigger than ~500.
pic is resized, if height is bigger than ~500.

when file saves, plugin creates helper file with extention .cuda-pic (in the same dir),
it is JSON file with info about inserted pictures.
pictures are saved in Base64 encoding here. so helper file is big.
on opening file, plugin reads this helper file, and re-adds pictures from it.
it creates picture files in the temp-folder.

during editing, if you insert/delete lines, pics are glued to their original lines.
they're deleted only if you delete their lines, or use plugin's commands to delete pics.


author: Alexey (CudaText)
license: MIT
