import bpy
from mathutils import Matrix, Vector
from ...utility import math as hops_math

from ... preferences import get_preferences

from ... ui_framework.master import Master
from ... ui_framework.utils.mods_list import get_mods_list
from ... ui_framework.graphics.draw import render_text, render_quad, draw_border_lines, render_image, draw_2D_lines
from ... ui_framework.graphics.load import load_image_file
from ... ui_framework.utils.geo import get_blf_text_dims
from ... ui_framework.utils.checks import is_mouse_in_quad
from ... addon.utility.screen import dpi_factor

from ... utility.base_modal_controls import Base_Modal_Controls

# Cursor Warp imports
from ... utils.toggle_view3d_panels import collapse_3D_view_panels
from ... utils.modal_frame_drawing import draw_modal_frame
from ... utils.cursor_warp import mouse_warp
from ... addon.utility import method_handler


class Dims:
    def __init__(self):
        
        # Bounds
        self.bot_left  = (0,0)
        self.top_left  = (0,0)
        self.top_right = (0,0)
        self.bot_right = (0,0)

        # Spacing
        self.padding = 8 * dpi_factor(min=.25)


class Colors:
    def __init__(self):
        self.highlight_color = get_preferences().color.Hops_UI_highlight_color
        self.cell_bg_color   = get_preferences().color.Hops_UI_cell_background_color
        self.border_color    = get_preferences().color.Hops_UI_border_color
        self.hover_color     = get_preferences().color.Hops_UI_mouse_over_color
        self.font_color      = get_preferences().color.Hops_UI_text_color


class Menu:
    def __init__(self, context):

        # Composition
        self.dims = Dims()
        self.colors = Colors()

        # Underlines
        self.line_thickness = 2
        self.top_divider_verts = []
        self.bot_divider_verts = []

        # Spacing
        factor = dpi_factor(min=.25)
        self.left_spacing = 110 * factor
        self.top_spacing  = 160 * factor

        # Screen
        self.screen_width = context.area.width
        self.screen_height = context.area.height

        # Inputs
        self.input_pressure     = Input_Field(label_text="PRESSURE", ID="PRESSURE")
        self.shrink_pressure    = Input_Field(label_text="SHRINK",   ID="SHRINK")
        self.timespane_pressure = Input_Field(label_text="TIMESPAN", ID="TIMESPAN")
        self.input_gravity      = Input_Field(label_text="GRAVITY",  ID="GRAVITY")

        # Buttons
        self.button_rewind = Button(image_name="rewind")
        self.button_play   = Button(image_name="play")
        self.button_pause  = Button(image_name="pause")
        self.button_reset  = Button(image_name="restart")
        self.button_apply  = Button(text="APPLY")
        self.button_finish = Button(text="✓")

        # Button configs
        self.button_apply.stay_active = True
        self.button_reset.stay_active = True

        # States
        self.show_play = True
        self.locked = False
        self.mouse_over = False

        # Move bracket
        self.move_bracket = Move_Bracket(context)

        # Build
        self.__setup_dims()
        self.move_bracket.setup()


    def __setup_dims(self):
        
        x = self.move_bracket.pos[0]
        y = self.move_bracket.pos[1]
        width = 0
        height = 0

        # Input width
        widest_input = max([self.input_pressure.total_width, self.shrink_pressure.total_width, self.timespane_pressure.total_width, self.input_gravity.total_width])

        # Get total width of the window
        buttons = [self.button_reset, self.button_play, self.button_rewind, self.button_apply, self.button_finish]
        for button in buttons:
            width += button.total_width
        width += self.dims.padding * 7

        # Input : Height
        height += sum([self.input_pressure.total_height, self.shrink_pressure.total_height, self.timespane_pressure.total_height, self.input_gravity.total_height])

        # Bottom Divider
        height += self.line_thickness + self.dims.padding * 4

        # Button : Height
        buttons = [self.button_reset.total_height, self.button_play.total_height, self.button_pause.total_height, self.button_rewind.total_height, self.button_apply.total_height, self.button_finish.total_height]
        height += max(buttons) + self.dims.padding

        self.move_bracket.height = height - self.dims.padding

        # Top divider
        # line_y = y - label_height - self.dims.padding * 2
        line_y = y - self.dims.padding * 2
        self.top_divider_verts = [
            (x + self.dims.padding, line_y),
            (x + width - self.dims.padding, line_y)]

        # Set overall dimensions
        self.dims.bot_left  = (x        , y - height)
        self.dims.top_left  = (x        , y)
        self.dims.top_right = (x + width, y)
        self.dims.bot_right = (x + width, y - height)

        x += self.dims.padding
        y -= self.dims.padding

        # Inputs : PRESSURE
        self.input_pressure.dims.bot_left  = (x               , y - self.input_pressure.total_height)
        self.input_pressure.dims.top_left  = (x               , y)
        self.input_pressure.dims.top_right = (x + widest_input, y)
        self.input_pressure.dims.bot_right = (x + widest_input, y - self.input_pressure.total_height)
        self.input_pressure.build_input_box()

        y -= self.input_pressure.total_height

        # Inputs : SHRINK
        self.shrink_pressure.dims.bot_left  = (x               , y - self.shrink_pressure.total_height)
        self.shrink_pressure.dims.top_left  = (x               , y)
        self.shrink_pressure.dims.top_right = (x + widest_input, y)
        self.shrink_pressure.dims.bot_right = (x + widest_input, y - self.shrink_pressure.total_height)
        self.shrink_pressure.build_input_box()

        y -= self.shrink_pressure.total_height

        # Inputs : TIMESPAN
        self.timespane_pressure.dims.bot_left  = (x               , y - self.timespane_pressure.total_height)
        self.timespane_pressure.dims.top_left  = (x               , y)
        self.timespane_pressure.dims.top_right = (x + widest_input, y)
        self.timespane_pressure.dims.bot_right = (x + widest_input, y - self.timespane_pressure.total_height)
        self.timespane_pressure.build_input_box()

        y -= self.timespane_pressure.total_height

        # Inputs : GRAVITY

        self.input_gravity.dims.bot_left  = (x               , y - self.input_gravity.total_height)
        self.input_gravity.dims.top_left  = (x               , y)
        self.input_gravity.dims.top_right = (x + widest_input, y)
        self.input_gravity.dims.bot_right = (x + widest_input, y - self.input_gravity.total_height)
        self.input_gravity.build_input_box()

        # Reset x
        x -= self.dims.padding

        # Bot divider
        line_y = self.input_gravity.dims.bot_right[1] - self.dims.padding
        self.bot_divider_verts = [
            (x + self.dims.padding, line_y),
            (x + width - self.dims.padding, line_y)]

        # Buttons
        buttons = [self.button_rewind, self.button_play, self.button_reset]

        x = self.dims.bot_left[0] + self.dims.padding
        y = self.dims.bot_left[1] + self.dims.padding

        for button in buttons:
            width = button.total_width
            height = button.total_height
            button.dims.bot_left  = (x        , y)
            button.dims.top_left  = (x        , y + height)
            button.dims.top_right = (x + width, y + height)
            button.dims.bot_right = (x + width, y)
            x += width + self.dims.padding

        # Copy over for this button
        self.button_pause.dims.bot_left  = self.button_play.dims.bot_left
        self.button_pause.dims.top_left  = self.button_play.dims.top_left
        self.button_pause.dims.top_right = self.button_play.dims.top_right
        self.button_pause.dims.bot_right = self.button_play.dims.bot_right

        # Finish button
        x = self.dims.bot_right[0] - self.dims.padding
        width = self.button_finish.total_width
        y = self.dims.bot_right[1] + self.dims.padding
        height = self.button_finish.total_height

        self.button_finish.dims.bot_left  = (x - width, y)
        self.button_finish.dims.top_left  = (x - width, y + height)
        self.button_finish.dims.top_right = (x        , y + height)
        self.button_finish.dims.bot_right = (x        , y)

        # Apply button
        x = self.button_finish.dims.bot_left[0]
        width = self.button_apply.total_width

        self.button_apply.dims.bot_left  = (x - width, y)
        self.button_apply.dims.top_left  = (x - width, y + height)
        self.button_apply.dims.top_right = (x        , y + height)
        self.button_apply.dims.bot_right = (x        , y)


    def update(self, context, event, op):

        # Move bracket
        if self.locked == False:
            self.move_bracket.update(context, event)
            if self.move_bracket.mouse_over:
                self.mouse_over = True
            if self.move_bracket.locked:
                self.__setup_dims()
                self.mouse_over = True
                return

        # Inputs
        set_back = self.button_reset.active
        self.input_pressure.update(context, event, op, set_back)
        self.shrink_pressure.update(context, event, op, set_back)
        self.timespane_pressure.update(context, event, op, set_back)
        self.input_gravity.update(context, event, op, set_back)

        self.locked = any([self.input_pressure.locked, self.shrink_pressure.locked, self.timespane_pressure.locked, self.input_gravity.locked])

        # Tabbed finish
        if self.input_pressure.tabbed_finish:
            self.input_pressure.tabbed_finish = False
            self.shrink_pressure.locked = True

        elif self.shrink_pressure.tabbed_finish:
            self.shrink_pressure.tabbed_finish = False
            self.timespane_pressure.locked = True
            
        elif self.timespane_pressure.tabbed_finish:
            self.timespane_pressure.tabbed_finish = False
            self.input_gravity.locked = True

        elif self.input_gravity.tabbed_finish:
            self.input_gravity.tabbed_finish = False

        # Buttons
        buttons = [self.button_reset, self.button_rewind, self.button_apply, self.button_finish]
        for button in buttons: button.update(context, event)

        self.show_play = context.screen.is_animation_playing

        if self.show_play:
            self.button_pause.update(context, event)
        else:
            self.button_play.update(context, event)

        mouse_pos = (event.mouse_region_x, event.mouse_region_y)
        self.mouse_over = is_mouse_in_quad((self.dims.top_left, self.dims.bot_left, self.dims.top_right, self.dims.bot_right), mouse_pos)


    def shut_down(self):

        # Remove images
        buttons = [self.button_reset,self.button_play,self.button_pause,self.button_rewind,self.button_apply,self.button_finish]
        for button in buttons: button.shut_down()


    def draw_2d(self):

        self.move_bracket.draw_2d()

        # Background
        render_quad(quad=(self.dims.top_left, self.dims.bot_left, self.dims.top_right, self.dims.bot_right), color=self.colors.cell_bg_color, bevel_corners=True)
        draw_border_lines(vertices=[self.dims.top_left, self.dims.bot_left, self.dims.top_right, self.dims.bot_right], width=1, color=self.colors.border_color, format_lines=True)

        # Inputs
        inputs = [self.input_pressure, self.shrink_pressure, self.timespane_pressure, self.input_gravity]
        for _input in inputs: _input.draw_2d()

        # Divider
        draw_2D_lines(vertices=self.bot_divider_verts, width=self.line_thickness, color=self.colors.border_color)

        # Buttons
        buttons = [self.button_reset, self.button_rewind, self.button_apply, self.button_finish]
        for button in buttons: button.draw_2d()

        if self.show_play:
            self.button_pause.draw_2d()
        else:
            self.button_play.draw_2d()


class Move_Bracket:
    def __init__(self, context):
        self.vert_dims = Dims()
        self.hori_dims = Dims()

        self.colors = Colors()

        self.screen_width = context.area.width
        self.screen_height = context.area.height

        self.factor = dpi_factor(min=.25)

        self.left_spacing = 150 * self.factor
        self.top_spacing  = 250 * self.factor

        # self.pos = (self.left_spacing, self.screen_height - self.top_spacing)
        self.pos = get_preferences().ui.cloth_pos

        self.width   = 130 * self.factor
        self.height  = 135 * self.factor
        self.thick   = 6   * self.factor
        self.padding = 6   * self.factor

        self.locked = False
        self.mouse_offset = (0,0)
        self.mouse_over = False

        self.setup()
        self.clamp(context)


    def update(self, context, event):

        if self.locked == True:
            self.locked_move(context, event)
            self.setup()

        mouse_pos = (event.mouse_region_x, event.mouse_region_y)
        over_vert = is_mouse_in_quad((self.vert_dims.top_left, self.vert_dims.bot_left, self.vert_dims.top_right, self.vert_dims.bot_right), mouse_pos, tolerance=14 * self.factor)
        over_hori = is_mouse_in_quad((self.hori_dims.top_left, self.hori_dims.bot_left, self.hori_dims.top_right, self.hori_dims.bot_right), mouse_pos, tolerance=14 * self.factor)

        if over_vert or over_hori:
            self.mouse_over = True
            if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                self.locked = True
                self.mouse_offset = (self.pos[0] - mouse_pos[0], self.pos[1] - mouse_pos[1])
        else:
            self.mouse_over = False


    def locked_move(self, context, event):
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            self.locked = False
            return

        mouse_pos = (event.mouse_region_x, event.mouse_region_y)
        self.pos = (mouse_pos[0] + self.mouse_offset[0], mouse_pos[1] + self.mouse_offset[1])
        self.clamp(context)


    def clamp(self, context):

        min_x = self.padding + self.thick
        if self.pos[0] < min_x:
            self.pos = (min_x, self.pos[1])

        max_x = self.screen_width - 210 * self.factor
        if self.pos[0] > max_x:
            self.pos = (max_x, self.pos[1])

        min_y = 160 * self.factor
        if self.pos[1] < min_y:
            self.pos = (self.pos[0], min_y)

        max_y = self.screen_height - 20 * self.factor
        if self.pos[1] > max_y:
            self.pos = (self.pos[0], max_y)

        get_preferences().ui.cloth_pos = self.pos
    

    def setup(self):

        # Vertical
        pos_x = self.pos[0] - self.padding
        pos_y = self.pos[1] - self.padding * 2
        self.vert_dims.bot_left  = (pos_x - self.thick, pos_y - self.height)
        self.vert_dims.top_left  = (pos_x - self.thick, pos_y)
        self.vert_dims.top_right = (pos_x             , pos_y)
        self.vert_dims.bot_right = (pos_x             , pos_y - self.height)

        # Horizontal
        pos_x = self.pos[0] - self.padding - self.thick
        pos_y = self.vert_dims.bot_left[1]
        self.hori_dims.bot_left  = (pos_x             , pos_y - self.thick)
        self.hori_dims.top_left  = (pos_x             , pos_y)
        self.hori_dims.top_right = (pos_x + self.width, pos_y)
        self.hori_dims.bot_right = (pos_x + self.width, pos_y - self.thick)


    def draw_2d(self):
        if self.mouse_over or self.locked:
            #color = self.colors.hover_color if self.mouse_over else self.colors.border_color
            color = self.colors.border_color
            render_quad(quad=(self.vert_dims.top_left, self.vert_dims.bot_left, self.vert_dims.top_right, self.vert_dims.bot_right), color=color, bevel_corners=False)
            render_quad(quad=(self.hori_dims.top_left, self.hori_dims.bot_left, self.hori_dims.top_right, self.hori_dims.bot_right), color=color, bevel_corners=False)


class Button:
    def __init__(self, text="", image_name=""):

        # Composition
        self.dims = Dims()
        self.colors = Colors()

        # Event
        self.func = None
        self.params = None

        # Auto generated dims
        factor = dpi_factor(min=.25)
        self.total_width = 28 * factor
        self.total_height = 28 * factor

        # Drawing
        self.text = None
        self.image = None

        if text != "":
            self.text = text
        elif image_name != "":
            self.image = load_image_file(filename=image_name)

        # Font
        self.font_size = 14
        
        # State
        self.mouse_over = False
        self.stay_active = False
        self.active = False

        # Build
        self.__setup_dims()


    def __setup_dims(self):

        if self.text != None:
            self.total_width = get_blf_text_dims(self.text, self.font_size)[0] + self.dims.padding * 2


    def update(self, context, event):
        mouse_pos = (event.mouse_region_x, event.mouse_region_y)
        self.mouse_over = is_mouse_in_quad((self.dims.top_left, self.dims.bot_left, self.dims.top_right, self.dims.bot_right), mouse_pos)

        if self.mouse_over:
            if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                if self.stay_active: self.active = not self.active

                # Function call
                if self.func == None: return
                if self.params != None: self.func(*self.params)
                else: self.func()


    def shut_down(self):
        if self.image != None:
            try: bpy.data.images.remove(self.image)
            except: pass


    def draw_2d(self):

        # Box
        color = self.colors.hover_color if self.mouse_over or self.active else self.colors.cell_bg_color
        render_quad(quad=(self.dims.top_left, self.dims.bot_left, self.dims.top_right, self.dims.bot_right), color=color, bevel_corners=True)
        draw_border_lines(vertices=[self.dims.top_left, self.dims.bot_left, self.dims.top_right, self.dims.bot_right], width=1, color=self.colors.border_color, format_lines=True)

        # Text
        if self.text != None:
            pos = (self.dims.bot_left[0] + self.dims.padding, self.dims.bot_left[1] + self.dims.padding)
            render_text(text=self.text, position=pos, size=self.font_size, color=self.colors.font_color)

        # Image
        elif self.image != None:
            render_image(image=self.image, verts=[self.dims.bot_left, self.dims.bot_right, self.dims.top_right, self.dims.top_left])


class Input_Field:
    def __init__(self, label_text="", ID=""):

        # Composition
        self.dims = Dims()
        self.colors = Colors()

        # Auto generated dims
        self.total_width = 0
        self.total_height = 0

        # Label
        self.ID = ID
        self.label_font_size = 14
        self.label_text = label_text

        # Input
        self.input_font_size = 12
        self.value = "0000000.0000000"
        self.input_dims = Dims()
        self.input_width = 0

        # Entry system
        self.entry_string = ""
        self.set_back = False

        # State
        self.locked = False
        self.mouse_over = False
        self.tabbed_finish = False

        # Build
        self.__setup_dims()


    def __setup_dims(self):

        # Label
        label_dims = get_blf_text_dims(self.label_text, self.label_font_size)
        label_width = label_dims[0] + self.dims.padding * 2
        label_height = label_dims[1] + self.dims.padding * 2

        # Input
        input_dims = get_blf_text_dims(self.value, self.input_font_size)
        input_width = input_dims[0] + self.dims.padding * 2
        input_height = input_dims[1] + self.dims.padding * 2
        self.input_width = input_width

        # Total
        self.total_width = label_width + input_width
        self.total_height = label_height if label_height > input_height else input_height


    def build_input_box(self):
        self.input_dims.bot_left  = (self.dims.bot_right[0] - self.input_width, self.dims.bot_left[1])
        self.input_dims.top_left  = (self.dims.bot_right[0] - self.input_width, self.dims.top_left[1])
        self.input_dims.top_right = (self.dims.bot_right[0]                   , self.dims.top_right[1])
        self.input_dims.bot_right = (self.dims.bot_right[0]                   , self.dims.bot_right[1])


    def update(self, context, event, op, set_back=False):

        self.set_back = set_back

        if self.locked:
            self.__update_locked_state(event, op)
            return True
        else:
            self.entry_string = ""
            self.tabbed_finish = False

            mod = op.cloth_mods[0][0]
            obj = op.cloth_mods[0][1]

            # Set the value
            if self.ID == "PRESSURE":
                val = getattr(mod.settings, "uniform_pressure_force")
                self.value = "{:.4f}".format(val)

            elif self.ID == "SHRINK":
                val = getattr(mod.settings, "shrink_min")
                self.value = "{:.4f}".format(val)

            elif self.ID == "TIMESPAN":
                val = getattr(mod.settings, "time_scale")
                self.value = "{:.4f}".format(val)

            elif self.ID == "GRAVITY":
                val = getattr(mod.settings.effector_weights, "gravity")
                self.value = "{:.4f}".format(val)

        mouse_pos = (event.mouse_region_x, event.mouse_region_y)
        self.mouse_over = is_mouse_in_quad((self.input_dims.top_left, self.input_dims.bot_left, self.input_dims.top_right, self.input_dims.bot_right), mouse_pos)

        if self.mouse_over:

            value = 0
            if event.shift:
                if self.ID == "PRESSURE":
                    value = 1
                elif self.ID == "SHRINK":
                    value = .1
                elif self.ID == "TIMESPAN":
                    value = .05
                elif self.ID == "GRAVITY":
                    value = .5
            else:
                if self.ID == "PRESSURE":
                    value = .1
                elif self.ID == "SHRINK":
                    value = .05
                elif self.ID == "TIMESPAN":
                    value = .1
                elif self.ID == "GRAVITY":
                    value = 1

            if event.type == 'WHEELUPMOUSE':
                self.__set_value(op, val=value, add=True)

            elif event.type == 'WHEELDOWNMOUSE':
                self.__set_value(op, val=-value, add=True)

            if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                self.value = "0"
                self.entry_string = ""
                self.locked = True

        return False


    def __update_locked_state(self, event, op):

        if event.type == 'TIMER':
            return

        valid = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', '-'}

        if event.ascii in valid and event.value == 'PRESS':
            # Decimal
            decimal_blocked = False
            if '.' in self.entry_string and event.ascii == '.':
                decimal_blocked = True
            
            # Append text
            if decimal_blocked == False:
                self.entry_string += str(event.ascii)

            # Negative
            if self.entry_string.count('-') > 1:
                self.entry_string = self.entry_string.replace('-', '')
            elif self.entry_string.count('-') == 1:
                self.entry_string = self.entry_string.replace('-', '')
                self.entry_string = '-' + self.entry_string

        # Finish
        if event.type in {'RET', 'NUMPAD_ENTER', 'SPACE', 'LEFTMOUSE', 'TAB'} and event.value == 'PRESS':
            if event.type == 'TAB':
                self.tabbed_finish = True

            set_val = 0
            try:
                set_val = float(self.entry_string)
            except:
                set_val = None

            # Set the value
            if set_val != None:
                self.__set_value(op, val=set_val, add=False)

            self.entry_string = ""
            self.locked = False

        elif event.type == 'BACK_SPACE' and event.value == 'PRESS':
            self.entry_string = self.entry_string[:-1]


    def __set_value(self, op, val, add=False):

        if self.set_back:
            op.restart()


        if self.ID == "PRESSURE":
            for item in op.cloth_mods:
                mod = item[0]
                if add:
                    attr = getattr(mod.settings, "uniform_pressure_force")
                    setattr(mod.settings, "uniform_pressure_force", attr + val)
                else:
                    setattr(mod.settings, "uniform_pressure_force", val)

        elif self.ID == "SHRINK":
            for item in op.cloth_mods:
                mod = item[0]
                if add:
                    attr = getattr(mod.settings, "shrink_min")
                    setattr(mod.settings, "shrink_min", attr + val)
                else:
                    setattr(mod.settings, "shrink_min", val)
                    
        elif self.ID == "TIMESPAN":
            for item in op.cloth_mods:
                mod = item[0]
                if add:
                    attr = getattr(mod.settings, "time_scale")
                    setattr(mod.settings, "time_scale", attr + val)
                else:
                    setattr(mod.settings, "time_scale", val)

        elif self.ID == "GRAVITY":
            for item in op.cloth_mods:
                mod = item[0]
                if add:
                    attr = getattr(mod.settings.effector_weights, "gravity")
                    setattr(mod.settings.effector_weights, "gravity", attr + val)
                else:
                    setattr(mod.settings.effector_weights, "gravity", val)


    def draw_2d(self):

        # Label
        pos = (self.dims.bot_left[0] + self.dims.padding, self.dims.bot_left[1] + self.dims.padding)
        render_text(text=self.label_text, position=pos, size=self.label_font_size, color=self.colors.font_color)

        # Box
        color = self.colors.hover_color if self.mouse_over or self.locked else self.colors.cell_bg_color
        render_quad(quad=(self.input_dims.top_left, self.input_dims.bot_left, self.input_dims.top_right, self.input_dims.bot_right), color=color, bevel_corners=True)
        draw_border_lines(vertices=[self.input_dims.top_left, self.input_dims.bot_left, self.input_dims.top_right, self.input_dims.bot_right], width=1, color=self.colors.border_color, format_lines=True)

        # Input
        pos = (self.input_dims.bot_left[0] + self.dims.padding, self.input_dims.bot_left[1] + self.dims.padding)
        text = self.entry_string if self.locked else str(self.value)
        render_text(text=text, position=pos, size=self.input_font_size, color=self.colors.font_color)


class HOPS_OT_AdjustClothOperator(bpy.types.Operator):
    bl_idname = "hops.adjust_cloth"
    bl_label = "Adjust Cloth"
    bl_options = {'REGISTER', 'UNDO', 'BLOCKING'}
    bl_description = """Placeholder"""

    numpad_map = {
        'NUMPAD_0' : 'ZERO' ,
        'NUMPAD_1' : 'ONE'  ,
        'NUMPAD_2' : 'TWO'  ,
        'NUMPAD_3' : 'THREE',
        'NUMPAD_4' : 'FOUR' ,
        'NUMPAD_5' : 'FIVE'}

    shrink_presets = {
        'ZERO' : 0 ,
        'ONE'  : -0.1, 
        'TWO'  : -0.3, 
        'THREE': -1.5, 
        'FOUR' : -2.0, 
        'FIVE' : -5.0}

    pressure_presets = {
        'ZERO' : 0,
        'ONE'  : 1, 
        'TWO'  : 2, 
        'THREE': 5, 
        'FOUR' : 10, 
        'FIVE' : 15}

    @classmethod
    def poll(cls, context):
        return context.selected_objects
    

    def invoke(self, context, event):

        self.param_names = {
            'uniform_pressure_force' : 'Pressure',
            'shrink_min' :  'Shrinking Factor',
            'time_scale' : 'Speed Multiplier'
        }

        self.params = list(self.param_names.keys())

        self.active_param = self.params[0]
        self.numbers = set()

        self.numbers.update(self.numpad_map.keys())
        self.numbers.update(self.numpad_map.values())

        self.cloth_mods = []
        self.cloth_back = []
        self.active_mod = None

        for obj in context.selected_objects:
            mod = self.get_cloth(obj)
            if mod:
                self.cloth_mods.append((mod, obj))

        if not self.cloth_mods:
            self.report({'INFO'}, "No Cloth modifiiers to adjust")
            return {'CANCELLED'}

        if not self.active_mod:
            self.active_mod = self.cloth_mods[0][0]

        for item in self.cloth_mods:
            mod = item[0]
            self.cloth_back.append([ getattr(mod.settings, name) for name in self.params])
        
        # UI Panel
        self.menu = Menu(context)

        self.menu.button_rewind.func = self.restart
        self.menu.button_rewind.params = None

        self.menu.button_play.func = bpy.ops.screen.animation_play
        self.menu.button_play.params = None

        self.menu.button_pause.func = bpy.ops.screen.animation_play
        self.menu.button_pause.params = None

        self.menu.button_reset.func = None
        self.menu.button_reset.params = None

        self.menu.button_apply.func = None
        self.menu.button_apply.params = None

        self.menu.button_finish.func = self.menu_set_exit
        self.menu.button_finish.params = None

        # UI Props
        self.confirmed_exit = False

        # States
        self.frozen = True

        # Base Systems
        self.master = Master(context=context)
        self.master.only_use_fast_ui = True
        self.base_controls = Base_Modal_Controls(context, event)
        self.original_tool_shelf, self.original_n_panel = collapse_3D_view_panels()
        self.draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.safe_draw_shader, (context,), 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


    def modal(self, context, event):

        # Update menu
        if self.frozen:
            if event.type != 'TIMER':
                self.menu.update(context, event, self)

        # Menu check box
        if self.confirmed_exit:
            return self.confirm_exit()

        # Base Systems
        self.master.receive_event(event=event)
        self.base_controls.update(context, event)
        if not self.frozen:
            mouse_warp(context, event)

        # Pass
        if self.base_controls.pass_through:
            return {'PASS_THROUGH'}

        # Assign value
        if self.base_controls.mouse:
            if not self.frozen:
                for item in self.cloth_mods:
                    mod = item[0]
                    attr = getattr(mod.settings, self.active_param)
                    setattr(mod.settings, self.active_param, attr + self.base_controls.mouse)

        # Switch attribute
        elif self.base_controls.scroll:
            if not self.frozen:
                self.active_param = self.params[ (self.params.index(self.active_param) + self.base_controls.scroll ) % len(self.params)]
                self.report({'INFO'}, F"Adjusting:{self.param_names[self.active_param]}")

        # Toggle animation play
        elif event.type == 'S' and event.value == 'PRESS':
            bpy.ops.screen.animation_play()

        # Toggle animation play
        elif event.type == 'SPACE' and event.value == 'PRESS' and event.shift:
            bpy.ops.screen.animation_play()

        # Jump to frame 1
        elif event.type == 'R' and event.value == 'PRESS':
            self.restart()
        
        # Freeze
        elif event.type == 'F' and event.value == 'PRESS':
            self.frozen = not self.frozen
        
        # Presets
        elif event.type in self.numbers and event.value == 'PRESS':
            key = self.numpad_map[event.type] if event.type in self.numpad_map else event.type
            value_map = None

            if self.active_param == 'uniform_pressure_force':
                value_map = self.pressure_presets

            elif self.active_param == 'shrink_min':
                value_map = self.shrink_presets                

            if value_map:
                value  =  value_map[key]
                if event.shift:
                    value *=-1
                self.set_params(self.active_param, value)
        
        # Invert value
        elif event.type == 'X' and event.value == 'PRESS':
            self.change_params(self.active_param , -1, lambda attr, val: attr*val)

        # Confirm Exit
        if not event.shift:
            apply_exit = True if event.ctrl and event.type == 'SPACE' and event.value == 'PRESS' else False
            if self.base_controls.confirm or apply_exit:
                if not self.menu.mouse_over and not self.menu.locked:
                    if apply_exit: self.apply_mods()
                    return self.confirm_exit()

        # Cancel Exit
        if self.base_controls.cancel:
            self.menu.shut_down()
            self.remove_shader()
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()

            # Stop the animation
            if bpy.context.screen.is_animation_playing:
                bpy.ops.screen.animation_play()
            
            # Revert mods
            for item, back in zip(self.cloth_mods, self.cloth_back):
                for name, val in zip(self.param_names.keys(), back):
                    mod = item[0]
                    setattr(mod.settings, name, val)
            return {'CANCELLED'}

        self.draw_ui(context)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}


    def draw_ui(self, context):

        self.master.setup()
        if self.master.should_build_fast_ui():

            # Main
            win_list = []
            if get_preferences().ui.Hops_modal_fast_ui_loc_options != 1:
                if not self.frozen:
                    win_list.append("{:.3f}".format(getattr(self.active_mod.settings, self.active_param)))
                else:
                    win_list.append("Window Mode")
                
            else:
                if not self.frozen:
                    win_list.append(self.param_names[self.active_param])
                    win_list.append("{:.3f}".format(getattr(self.active_mod.settings, self.active_param)))
                else:
                    win_list.append("Window Mode")

            # Help
            help_items = {"GLOBAL" : [], "STANDARD" : []}

            help_items["GLOBAL"] = [
                ("M", "Toggle mods list"),
                ("H", "Toggle help"),
                ("~", "Toggle UI Display Type"),
                ("O", "Toggle viewport rendering")]

            h_append = help_items["STANDARD"].append

            h_append(["Shift Space", "Toggle play timeline"])
            h_append(["Ctrl Space", "Apply mods and Exit"])
            if not self.frozen:
                h_append(["0", "set value to 0"])

            var = "ON" if self.frozen else "OFF"
            h_append(["F", f"Mouse Controls {var}"])

            h_append(["X", "Set value to negative"])
            h_append(["1 - 5", "Value presets; Shift for negative values"])
            h_append(["R", "Reset timeline"])
            h_append(["S", "Start/Play"])
            h_append(["LMB", "Apply"])
            h_append(["RMB", "Cancel"])
            if not self.frozen:
                h_append(["Scroll  ", "Cycle Parameter"])
                h_append(["Mouse   ", "Adjust Value"])

            # Mods
            mods_list = get_mods_list(mods=bpy.context.active_object.modifiers if context.active_object else [])
            self.master.receive_fast_ui(win_list=win_list, help_list=help_items, image="Tthick", mods_list=mods_list)

        self.master.finished()

    ####################################################
    #   UTILS
    ####################################################

    def restart(self):
        for item in self.cloth_mods:
            mod = item[0]
            mod.show_viewport = False
        bpy.ops.screen.frame_jump(end=False)
        
        for item in self.cloth_mods:
            mod = item[0]
            mod.show_viewport = True


    def confirm_exit(self):

        # Stop the animation
        if bpy.context.screen.is_animation_playing:
            bpy.ops.screen.animation_play()

        # Apply all mods up to the cloth mod
        if self.menu.button_apply.active:
            self.apply_mods()

        # Shut down
        self.menu.shut_down()
        self.remove_shader()
        collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
        self.master.run_fade()
        self.report({'INFO'}, "FINISHED")
        return {'FINISHED'}


    def menu_set_exit(self):
        self.confirmed_exit = True


    def apply_mods(self):

        for item in self.cloth_mods:
            mod, obj = item[0], item[1]
            bpy.context.view_layer.objects.active = obj

            for modifier in obj.modifiers:
                should_break = True if mod == modifier else False
                bpy.ops.object.modifier_apply(modifier=modifier.name)
                if should_break:
                    break


    def get_cloth(self, obj):
        for mod in reversed(obj.modifiers):
            if mod.type == 'CLOTH':
                if obj is bpy.context.active_object:
                    self.active_mod = mod
                return mod


    def set_params(self, name, val):
        for item in self.cloth_mods:
            mod = item[0]
            setattr(mod.settings, name, val)


    def change_params(self, name, val, func):
        for item in self.cloth_mods:
            mod = item[0]
            attr = getattr(mod.settings, name)
            setattr(mod.settings, name, func(attr, val))

    ####################################################
    #   SHADERS
    ####################################################

    def safe_draw_shader(self, context):
        method_handler(self.draw_shader,
            arguments = (context,),
            identifier = 'Cloth Shader',
            exit_method = self.remove_shader)


    def remove_shader(self):
        '''Remove shader handle.'''

        if self.draw_handle:
            self.draw_handle = bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle, "WINDOW")


    def draw_shader(self, context):
        '''Draw shader handle.'''

        if not self.frozen:
            draw_modal_frame(context)

        if self.frozen:
            self.menu.draw_2d()