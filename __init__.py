import os
import json
import tempfile
import zlib
import base64
from cudatext import *
from .imgsize import *

PIC_TAG = 0x1000 #minimal tag for api (CRC adds to tag)
BIG_SIZE = 500 #if width bigger, ask to resize
DIALOG_FILTER = 'Pictures|*.png;*.jpg;*.jpeg;*.jpe;*.gif;*.bmp;*.ico'
PRE = '[Insert Pics] '
MIN_H = 10 #limitations of api to gap height
MAX_H = 500-5

data_all = {}
temp_dir = tempfile.gettempdir()
id_img = image_proc(0, IMAGE_CREATE)


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

def get_helper_filename(fn):
    if fn:
        return fn+'.cuda-pic'


class Command:
    def insert_dlg(self):

        fn_ed = ed.get_filename()
        if not fn_ed:
            msg_status(PRE+'Needed named file')
            return

        fn = dlg_file(True, '', '', DIALOG_FILTER)
        if fn:
            self.insert_file(fn)


    def insert_file(self, fn):

        fn_ed = ed.get_filename()
        res = get_image_size(fn)
        if not res:
            msg_status(PRE+'Cannot detect picture sizes')
            return
        size_x, size_y = res

        if size_x>BIG_SIZE:
            res = dlg_input('Picture width is %d. Resize to width:' % size_x, str(BIG_SIZE))
            if res:
                new_x = int(res)
                size_y = size_y*new_x//size_x
                size_x = new_x

        x1, nline, x2, y2 = ed.get_carets()[0]

        crc = get_file_crc(fn)
        code = get_file_code(fn)
        ntag = PIC_TAG+crc

        self.add_dataitem(crc, fn_ed, size_x, size_y, os.path.basename(fn), code)
        self.add_pic(ed, nline, fn, size_x, size_y, ntag)
        ed.set_prop(PROP_MODIFIED, '1')
        msg_status(PRE+'Added "%s", %dx%d, line %d' % (os.path.basename(fn), size_x, size_y, nline))

    def insert_clp(self):

        fmt = app_proc(PROC_CLIP_ENUM, '')
        if not 'p' in fmt:
            msg_status(PRE+'Clipboard doesn\'t contain picture')
            return

        fn = os.path.join(temp_dir, 'cudatext_clipboard.png')
        if os.path.exists(fn):
            os.remove(fn)

        if not app_proc(PROC_CLIP_SAVE_PIC, fn):
            msg_status(PRE+'Cannot save clipboard to a file: '+fn)
            return

        self.insert_file(fn)


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

        global id_img
        if not image_proc(id_img, IMAGE_LOAD, fn):
            print(PRE+'Cannot load "%s"' % os.path.basename(fn))
            return

        new_y = None
        if size_y < MIN_H: new_y = MIN_H
        if size_y > MAX_H: new_y = MAX_H
        if new_y is not None:
            size_x = round(size_x/size_y*new_y)
            size_y = new_y

        id_bitmap, id_canvas = ed.gap(GAP_MAKE_BITMAP, size_x, size_y)
        canvas_proc(id_canvas, CANVAS_SET_BRUSH, color=0xffffff)
        canvas_proc(id_canvas, CANVAS_RECT_FILL, x=0, y=0, x2=size_x, y2=size_y)

        image_proc(id_img, IMAGE_PAINT_SIZED, (id_canvas, 0, 0, size_x, size_y))

        ed.gap(GAP_DELETE, nline, nline)
        ed.gap(GAP_ADD, nline, id_bitmap, tag=ntag)

        print(PRE+'"%s", %dx%d, line %d' % (os.path.basename(fn), size_x, size_y, nline+1))


    def count_pics(self, ed):

        gaps = ed.gap(GAP_GET_ALL, 0, 0)
        if not gaps: return 0

        cnt = 0
        for item in gaps:
            crc = item['tag']-PIC_TAG
            if crc>0:
                cnt += 1
        return cnt


    def del_cur(self):

        cnt1 = self.count_pics(ed)
        x1, nline, x2, y2 = ed.get_carets()[0]
        ed.gap(GAP_DELETE, nline, nline)

        cnt2 = self.count_pics(ed)
        if cnt1!=cnt2:
            ed.set_prop(PROP_MODIFIED, '1')


    def del_all(self):

        gaps = ed.gap(GAP_GET_ALL, 0, 0)
        if not gaps: return

        cnt = 0
        for item in gaps:
            y = item['line']
            tag = item['tag']
            if tag>PIC_TAG:
                ed.gap(GAP_DELETE, y, y)
                cnt += 1

        msg_status(PRE+'Removed %d pics' % cnt)
        if cnt>0:
            ed.set_prop(PROP_MODIFIED, '1')


    def on_open(self, ed_self):

        fn_ed = ed_self.get_filename()
        if not fn_ed: return
        fn_helper = get_helper_filename(fn_ed)
        if not os.path.isfile(fn_helper): return

        with open(fn_helper, encoding='utf8') as f:
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

        msg_status(PRE+'Loaded %d pics' % len(data_this))


    def on_save(self, ed_self):

        fn_ed = ed_self.get_filename()
        if not fn_ed: return
        fn_helper = get_helper_filename(fn_ed)
        if os.path.isfile(fn_helper):
            os.remove(fn_helper)

        gaps = ed_self.gap(GAP_GET_ALL, 0, 0)
        if not gaps: return

        data_ed = data_all.get(fn_ed, None)
        if not data_ed: return

        data_this = []
        for item in gaps:
            nline = item['line']
            ntag = item['tag']
            size_x, size_y = item['bitmap']
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
        with open(fn_helper, 'w', encoding='utf8') as f:
            f.write(json.dumps(data_this, indent=4))
