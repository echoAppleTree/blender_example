import bpy
from .. preferences import get_preferences
from .. utils.blender_ui import get_dpi_factor


confirm_events = {'SPACE', 'LEFTMOUSE', 'RET', 'NUMPAD_ENTER'}
cancel_events = {'ESC', 'RIGHTMOUSE'}
pass_through_events = {'MIDDLEMOUSE'}
increment_maps = {"WHEELUPMOUSE", 'NUMPAD_PLUS', 'EQUAL', 'UP_ARROW'}
decrement_maps = {"WHEELDOWNMOUSE", 'NUMPAD_MINUS', 'DOWN_ARROW', 'MINUS'}

class Base_Modal_Controls():

    def __init__(self, context, event):
        self.scroll  = None
        self.confirm = None
        self.cancel  = None
        self.mouse   = None
        self.pass_through = False
        self.tilde = None
        self.divisor = 1000
        self.divisor_shift = 10
        self.keyboard_increment = {'NUMPAD_PLUS', 'EQUAL', 'UP_ARROW'}
        self.keyboard_decrement = {'NUMPAD_MINUS', 'DOWN_ARROW', 'MINUS'}     
        self.update(context, event)
        
    def update(self, context, event, toggle_wire=True):
        self.mouse = mouse(event, divisor=self.divisor, divisor_shift= self.divisor_shift)
        self.confirm = confirm(event)
        self.cancel = cancel(event)
        self.pass_through = pass_through(event)
        self.scroll = scroll(event)
        self.tilde = tilde(context, event)

        # Toggle viewport display
        if event.type == "O" and event.value == "PRESS":
            types = ['WIREFRAME', 'SOLID', 'MATERIAL', 'RENDERED']
            index = types.index(context.space_data.shading.type)
            context.space_data.shading.type = types[(index + 1) % len(types)]

        # Toggle help
        if event.type == "H" and event.value == "PRESS":
            get_preferences().property.hops_modal_help = not get_preferences().property.hops_modal_help

        # Toggle overlays
        if self.tilde and event.shift == True:
            bpy.context.space_data.overlay.show_overlays = not bpy.context.space_data.overlay.show_overlays


def mouse(event, divisor = 1000, divisor_shift = 10):
    if event.type not in {'MOUSEMOVE', 'TRACKPADPAN'}:
        return 0
    modal_scale = get_preferences().ui.Hops_modal_scale
    delta = event.mouse_x - event.mouse_prev_x
    if bpy.app.version[1] > 91:
        divisor = divisor / (4.5 / get_dpi_factor())
    delta = modal_scale * delta / divisor / get_dpi_factor()
    if event.shift:
        delta = modal_scale * delta / divisor_shift / get_dpi_factor()

    if get_preferences().property.modal_handedness == 'LEFT':
        return -delta
    else:
        return delta


def confirm(event):
    return event.type in confirm_events and event.value == 'PRESS'


def cancel(event):
    return event.type in cancel_events and event.value == 'PRESS'


def pass_through(event):
    if bpy.context.preferences.inputs.use_mouse_emulate_3_button and event.alt and event.type == 'LEFTMOUSE':
        return True
    return event.type in pass_through_events or 'NDOF' in event.type


def scroll(event):

    if event.type == 'TRACKPADPAN':
        delta = event.mouse_y - event.mouse_prev_y
        if abs(delta) < 5: return 0
        if delta > 0: return 1
        elif delta < 0: return -1
        else: return 0

    scroll = 0
    if event.type in increment_maps:
        if event.value == 'PRESS':
            scroll = 1
    if event.type in decrement_maps:
        if event.value == 'PRESS':
            scroll = -1
    return scroll


def tilde(context, event):
    tilde = context.window_manager.keyconfigs.user.keymaps['3D View'].keymap_items['hops.tilde_remap']
    return keymap_item_reader(tilde, event)


def keymap_item_reader(kmi, event):

    if event.type == kmi.type and event.value == kmi.value:
        result=[True]
        if kmi.any:
            result = [event.ctrl, event.shift, event.alt, event.oskey]
            return any(result)
        else:
            if kmi.ctrl or kmi.oskey:
                result.append(event.ctrl)
            if kmi.shift:
                result.append(event.shift)
            if kmi.alt:
                result.append(event.alt)
            if kmi.oskey:
                result.append(event.oskey)
            if kmi.key_modifier != "NONE":
                result.append(event.type == kmi.key_modifier)

        return all (result)

    return False
