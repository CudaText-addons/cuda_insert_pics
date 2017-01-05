import os
import json
import tempfile
import zlib
import base64
from cudatext import *
from .imgsize import *

PIC_TAG = 0x1000 #minimal tag for api (CRC adds to tag)
BIG_SIZE = 500 #if width bigger, ask to resize
DIALOG_FILTER = 'Pictures|*.png;*.jpg;*.jpeg;*.jpe;*.gif'
API_OK = app_api_version()>='1.0.164'

data_all = {}
temp_dir = tempfile.gettempdir()


def get_file_crc(filename):
    s = open(filename, "rb").read()
    return zlib.crc32(s) & 0xFFFFFFFF

def get_file_code(filename):
    s = ''
    with open(filename, "rb") as f:
        s = base64.b64encode(f.read())
        s = s.decode()
    return s

def write_file_code(filename, s):
    s = s.encode()
    s = base64.b64decode(s)
    with open(filename, "wb") as f:
        f.write(s)


def get_notes_fn(fn):
    if fn:
        return fn+'.cuda-notes'


class Command:
    def insert_dlg(self):
    
        if not API_OK:
            msg_box('Insert Pics plugin needs newer app version', MB_OK+MB_ICONERROR)
            return
    
        fn = dlg_file(True, '', '', DIALOG_FILTER)
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

        crc = get_file_crc(fn)
        code = get_file_code(fn)
        ntag = PIC_TAG+crc
        
        self.add_dataitem(crc, ed.get_filename(), size_x, size_y, os.path.basename(fn), code)
        self.add_pic(ed, nline, fn, size_x, size_y, ntag)
        ed.set_prop(PROP_MODIFIED, '1')
        msg_status('Preview of "%s" as %dx%d, line %d' % (os.path.basename(fn), size_x, size_y, nline))


    def add_dataitem(self, crc, fn_ed, size_x, size_y, pic_fn, pic_data):

        if fn_ed not in data_all:
            data_all[fn_ed] = {}    
        
        data_all[fn_ed][crc] = {
          'size_x': size_x,
          'size_y': size_y,
          'pic_fn': pic_fn,
          'pic_data': pic_data,
          }


    def add_pic(self, ed, nline, fn, size_x, size_y, ntag):

        id_bitmap, id_canvas = ed.gap(GAP_MAKE_BITMAP, size_x, size_y)
        canvas_proc(id_canvas, CANVAS_SET_BRUSH, color=0xffffff)
        canvas_proc(id_canvas, CANVAS_RECT_FILL, x=0, y=0, x2=size_x, y2=size_y)
        canvas_proc(id_canvas, CANVAS_IMAGE_SIZED, x=0, y=0, x2=size_x, y2=size_y, text=fn)

        ed.gap(GAP_DELETE, nline, nline)
        ed.gap(GAP_ADD, nline, id_bitmap, tag=ntag)
        
        print('[Insert Pics] "%s", %dx%d, line %d' % (os.path.basename(fn), size_x, size_y, nline+1))


    def del_cur(self):

        x1, nline, x2, y2 = ed.get_carets()[0]
        ed.gap(GAP_DELETE, nline, nline)

    def del_all(self):

        l = ed.gap(GAP_GET_LIST, 0, 0)
        if not l: return

        cnt = 0
        for (y, tag, sizex, sizey) in l:
            if tag>=PIC_TAG:
                ed.gap(GAP_DELETE, y, y)
                cnt += 1
        msg_status('Removed %d pics' % cnt)


    def on_open(self, ed_self):
    
        if not API_OK: return
    
        fn_ed = ed_self.get_filename()
        if not fn_ed: return
        fn_notes = get_notes_fn(fn_ed)
        if not os.path.isfile(fn_notes): return

        with open(fn_notes, encoding='utf8') as f:
            data_this = json.load(f)
        if not data_this: return

        for item in data_this:
            nline = item['line']
            crc = item['crc']
            pic_fn = item['pic_fn']
            pic_data = item['pic_data']
            size_x = item['size_x']
            size_y = item['size_y']

            ntag = PIC_TAG+crc
            fn_temp = os.path.join(temp_dir, pic_fn)
            write_file_code(fn_temp, pic_data)

            self.add_dataitem(crc, fn_ed, size_x, size_y, pic_fn, pic_data)
            self.add_pic(ed_self, nline, fn_temp, size_x, size_y, ntag)

        msg_status('[Insert Pics] Loaded %d pics' % len(data_this))


    def on_save(self, ed_self):
    
        fn_ed = ed_self.get_filename()
        if not fn_ed: return
        fn_notes = get_notes_fn(fn_ed)
        if os.path.isfile(fn_notes):
            os.remove(fn_notes)

        gaps = ed_self.gap(GAP_GET_LIST, 0, 0)
        if not gaps: return
        
        data_ed = data_all.get(fn_ed, None)
        if not data_ed: return

        data_this = []
        for (nline, ntag, size_x, size_y) in gaps:
            crc = ntag-PIC_TAG
            if crc<=0: continue
            data_item = data_ed.get(crc, None)
            if data_item:
                data_this.append({
                  'crc': crc,
                  'line': nline,
                  'size_x': size_x,
                  'size_y': size_y,
                  'pic_fn': data_item['pic_fn'],
                  'pic_data': data_item['pic_data'],
                  })

        if not data_this: return
        with open(fn_notes, 'w', encoding='utf8') as f:
            f.write(json.dumps(data_this, indent=4))
