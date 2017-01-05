import os
import zlib
import base64
import json
from cudatext import *
from .imgsize import *

PIC_TAG = 2000 #uniq tag for api
BIG_SIZE = 600 #if width bigger, ask to resize

data_all = {}

def get_file_crc(filename):
    s = open(filename, "rb").read()
    return zlib.crc32(s) & 0xFFFFFFFF
    
def get_file_str(filename):
    s = ''
    with open(filename, "rb") as f:
        s = base64.b64encode(f.read())
        s = s.decode()
    return s    

def get_notes_fn(fn):
    if fn:
        return fn+'.cuda-notes'

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

        msg_status('Preview of "%s" as %dx%d, at line %d' % (os.path.basename(fn), size_x, size_y, nline))
        
        crc = get_file_crc(fn)
        ntag = PIC_TAG + crc
        data_all[crc] = {
          'ed_fn': ed.get_filename(),
          'pic_fn': os.path.basename(fn),
          'pic_data': get_file_str(fn),
          } 
        #print(data_all)
        
        ed.gap(GAP_DELETE, nline, nline)
        ed.gap(GAP_ADD, nline, id_bitmap, tag=ntag)
        

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
        data_all = {}
        pass
        
    def on_save(self, ed_self):
        fn = ed_self.get_filename()
        if not fn: return
        fn = get_notes_fn(fn)
        
        if os.path.isfile(fn):
            os.remove(fn)
        
        gaps = ed_self.gap(GAP_GET_LIST, 0, 0)
        if not gaps: return
        
        data_this = []
        for (nline, ntag, sizex, sizey) in gaps:
            ntag -= PIC_TAG
            if ntag<=0: continue 
            data_item = data_all.get(ntag, None)
            if data_item:
                data_this.append({
                  'crc': ntag,
                  'line': nline,
                  'pic_fn': data_item['pic_fn'],
                  'pic_data': data_item['pic_data'],
                  })
            
        if not data_this: return
        with open(fn, 'w', encoding='utf8') as f:
            f.write(json.dumps(data_this, indent=4))
