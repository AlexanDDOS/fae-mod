default persistent.current_bg = 'spaceroom'
default persistent.static_bg = False

#Spaceroom displayables

image mask_child:
    "images/cg/monika/child_2.png"
    xtile 2

image mask_mask:
    "images/cg/monika/mask.png"
    xtile 3

image mask_mask_flip:
    "images/cg/monika/mask.png"
    xtile 3 xzoom -1


image maskb:
    "images/cg/monika/maskb.png"
    xtile 3

image mask_test = AnimatedMask("#ff6000", "mask_mask", "maskb", 0.10, 32)
image mask_test2 = AnimatedMask("#ffffff", "mask_mask", "maskb", 0.03, 16)
image mask_test3 = AnimatedMask("#ff6000", "mask_mask_flip", "maskb", 0.10, 32)
image mask_test4 = AnimatedMask("#ffffff", "mask_mask_flip", "maskb", 0.03, 16)

image mask_2:
    "images/cg/monika/mask_2.png"
    xtile 3 subpixel True
    block:
        xoffset 1280
        linear 1200 xoffset 0
        repeat

image mask_3:
    "images/cg/monika/mask_3.png"
    xtile 3 subpixel True
    block:
        xoffset 1280
        linear 180 xoffset 0
        repeat

image monika_room = "mod_assets/images/bg/spaceroom.png"
#image monika_room_highlight:
#    "images/cg/monika/monika_room_highlight.png"
#    function monika_alpha
#
#
#image room_glitch = "images/cg/monika/monika_bg_glitch.png"
#
#image rm = LiveComposite((1280, 720), (0, 0), "mask_test", (0, 0), "mask_test2", pos = (0,380), zoom = 0.25)
#image rm2 = LiveComposite((1280, 720), (0, 0), "mask_test3", (0, 0), "mask_test4", pos = (600,380), zoom = 0.25)
#

init -8 python:
    def mix(a, b, c):
        """Mix b into a in the relation of c"""
        try:
            r = []
            for i in range(min(len(a), len(b))):
                r.append(mix(a[i], b[i], c))
            return r
        except TypeError:
            return a*(1-c) + b*c
    
    sky = Solid("#fff") #Universal sky image
        
    def get_sky_color(tod, tr = 0):
        sky = None
        if tod == 0:
            sky = (0x1c, 0x1c, 0x1d)
        elif tod == 1:
            sky = (0xff ,0xc6, 0x89)
        elif tod == 2:
            sky = (0x93, 0xc6, 0xf6)
        else:
            sky = (0xff, 0xa8, 0x98)
        if tr > 0:
            next_sky = get_sky_color((tod + 1) % 4, 0)
            return mix(sky, next_sky, tr)
        return sky 
    
    def draw_sky():
        tr = get_time_transition_factor()
        color = get_sky_color(get_time_of_day(), tr)
        color = "#%02x%02x%02x" % tuple(color)
        sky.color = Color(color)
        renpy.show("bg", what = sky, layer = 'bg', zorder = 0)
    
    class Background:
        defualt_matrix = im.matrix((
    1,0,0,0,0,
    0,1,0,0,0,
    0,0,1,0,0,
    0,0,0,1,0))
        def __init__(self, code, name, constructor = None, destructor = None):
            self.code = code
            self.sprites = {
                "table": SpriteInfo("table", code)
            }
            self.name = name
            self.constructor = constructor
            self.destructor = destructor
            self.matrices = [self.defualt_matrix] * 4 #[night,morning,day,evening]
            self.shown = False
            self.static = None
        
        def show(self, static = False, nc = False):
            if self.shown and static == self.static:
                return None
            if not self.constructor:
                raise ValueError("BG constructor must be definded")
            elif callable(self.constructor):
                self.shown = True
                self.static = static
                return self.constructor(self, static)
            else:
                self.shown = True
                self.static = static
                if nc:
                    renpy.call_in_new_context(self.constructor, self, static)
                else:
                    renpy.call(self.constructor, self, static)
        
        def hide(self, nc = False):
            if not self.constructor:
                raise ValueError("BG destructor must be definded")
            elif callable(self.destructor):
                self.shown = False
                self.static = None
                return self.destructor(self)
            else:
                self.shown = False
                self.static = None
                if nc:
                    renpy.call_in_new_context(self.destructor, self, static)
                else:
                    renpy.call(self.destructor)
        
        def get_current_matrix(self):
            tr = get_time_transition_factor()
            cm = self.matrices[get_time_of_day()]
            if tr == 0:
                return cm
            else:
                nm = self.matrices[(get_time_of_day() + 1) % 4]
                return mix(cm, nm, tr)
        
        def apply_current_matrix(self,img,**props):
            return im.MatrixColor(img,self.get_current_matrix(),**props)
    
    class BGList:
        def __init__(self):
            self.bgs = {}
            self.current_id = None
        
        def __setattr__(self, attr, value):
            if attr == 'current':
                persistent.current_bg = value
            else:
                self.__dict__[attr] = value
        
        def __getattr__(self, attr):
            if attr == 'current':
                return persistent.current_bg
        
        def __getitem__(self, index):
            return self.bgs[index]
        
        def __setitem__(self, index, value):
            self.bgs[index] = value
        
        def __iter__(self):
            return iter(self.bgs)
        
        def show(self, id = None, static = None, nc = False):
            if id == None:
                id = self.current_id
            if static is None:
                static = persistent.static_bg
            
            #if self.bgs[self.current].shown:
            #   self.bgs[self.current].hide() 
            
            r = self.bgs[id].show(static, nc)
            self.current_id = id
            return r
        
        def hide_current(self, change = False):
            if not self.current:
                raise ValueError("None BG is shown")
            r = self.bgs[self.current].hide()
            if not change:
                self.current = None
            return r
        
        @property
        def current(self):
            return self.bgs[self.current_id]
    
    backgrounds = BGList()
    
    def sroom_dyn(st, at, *args, **kwargs):
        bg = kwargs["bg"]
        draw_sky()
        frame = bg.apply_current_matrix("mod_assets/images/bg/spaceroom.png")
        if st % COLOR_STEP <= 1/60:
            renpy.free_memory() #Matrix creates sp much of garbage that its better to collect it manually
        return frame, COLOR_STEP
            
    def sroom_c(self, static = False):
        # if static:
            # renpy.show('monika_room_static', layer = 'bg')
        # else:
            # renpy.show('mask_2', layer = 'bg')
            # renpy.show('mask_3', layer = 'bg')
            # renpy.show('rm', layer = 'bg')
            # renpy.show('rm2', layer = 'bg')
            # renpy.show('monika_room', layer = 'bg')
            # renpy.show('monika_room_highlight', layer = 'bg')
        dd = DynamicDisplayable(sroom_dyn, bg = self)
        renpy.show("bg_room", what = dd, layer = 'bg', zorder = 2)
        
    def sroom_d(self):
        renpy.scene('bg')
    
    backgrounds['spaceroom'] = Background("spaceroom", "Spaceroom", sroom_c, sroom_d)
    backgrounds['spaceroom'].matrices[0] = im.matrix((
    0.3,0.1,0,0,0,
    0.075,0.4,0,0,0,
    0.075,0,0.55,0,0,
    0,0,0,1,0))
    backgrounds['spaceroom'].matrices[1] = im.matrix.tint(1, 0xc6/255, 0x89/255)
    backgrounds['spaceroom'].matrices[3] = im.matrix.tint(1, 0xa8/255, 0x98/255)
    backgrounds.current_id = "spaceroom"
