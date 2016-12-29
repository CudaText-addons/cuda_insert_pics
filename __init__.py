import os
from cudatext import *
from .imgsize import *

PIC_TAG = 101 #uniq tag for api
BIG_SIZE = 500 #if width bigger, ask to resize


class Command:
    def insert_dlg(self):
        fn = dlg_file(True, '', '', 'Picture files|*.png;*.jpg;*.jpeg;*.gif')
        if not fn: return
        
        res = get_image_size(fn)
        if not res:
            msg_status('Cannot detect picture sizes')
            return
        size_x, size_y = res
        
        if size_x>BIG_SIZE:
            res = dlg_input('Pic width: %d. Resize to:' % size_x, str(BIG_SIZE))
            if res:
                new_x = int(res)
                size_y = size_y*new_x//size_x
                size_x = new_x
        
        x1, nline, x2, y2 = ed.get_carets()[0]
        
        id_bitmap, id_canvas = ed.gap(GAP_MAKE_BITMAP, size_x, size_y)
        canvas_proc(id_canvas, CANVAS_SET_BRUSH, color=0xffffff)
        canvas_proc(id_canvas, CANVAS_RECT_FILL, x=0, y=0, x2=size_x, y2=size_y)
        canvas_proc(id_canvas, CANVAS_IMAGE_SIZED, x=0, y=0, x2=size_x, y2=size_y, text=fn)
        ed.gap(GAP_DELETE, nline, nline)
        ed.gap(GAP_ADD, nline, id_bitmap, tag=PIC_TAG)
        msg_status('Preview of "%s" as %dx%d, at line %d' % (os.path.basename(fn), size_x, size_y, nline))
        

    def del_cur(self):

        x1, nline, x2, y2 = ed.get_carets()[0]
        ed.gap(GAP_DELETE, nline, nline)
        
    def del_all(self):

        l = ed.gap(GAP_GET_LIST, 0, 0)
        if not l: return
        
        cnt = 0
        for (y, tag, sizex, sizey) in l:
            if tag==PIC_TAG:
                ed.gap(GAP_DELETE, y, y)
                cnt += 1
        msg_status('Removed %d pics' % cnt)
    
    def on_open(self, ed_self):
        pass
    def on_save(self, ed_self):
        pass
