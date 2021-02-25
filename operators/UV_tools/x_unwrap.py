import bpy
from bpy.props import FloatProperty, BoolProperty
from . uv_draw import hops_draw_uv
from ... utils.bmesh import selectSmoothEdges
from ... preferences import get_preferences
from ...ui_framework.operator_ui import Master

class HOPS_OT_XUnwrapF(bpy.types.Operator):
    bl_idname = "hops.xunwrap"
    bl_label = "XUnwrap"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = """Unwrap mesh using automated unwrapping and draw UVs in the 3d view
    CTRL - Only display UVs (No Unwrap)"""
    
    angle_limit:      FloatProperty(name="Angle limit", default=45, min=0.0, max=90)
    rmargin:          FloatProperty(name="Margin", default=0.0002, min=0.0, max=1)
    user_area_weight: FloatProperty(name="User area weight", default=0.03, min=0.0, max=1)
    rmethod:          BoolProperty(default=True)
    bweight_as_seams: BoolProperty(default=True)
    called_ui = False


    def __init__(self):
        HOPS_OT_XUnwrapF.called_ui = False

    @classmethod
    def poll(cls, context):
        selected = context.selected_objects
        object = context.active_object
        if object is None: return False
        if object.mode == "OBJECT" and any(obj.type == "MESH" for obj in selected):
            return True


    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.prop(self, "angle_limit")
        box.prop(self, 'bweight_as_seams', text="convert bevel weight to seams")
        box.prop(self, "rmargin")
        box.prop(self, "user_area_weight")
        box.prop(self, 'rmethod', text="use smart method")


    def invoke(self, context, event):

        # Call UV Draw op only
        if event.ctrl == True:
            bpy.ops.hops.draw_uv_launcher(use_selected_meshes=True)
            return {"FINISHED"}

        self.execute(context)
        #hops_draw_uv()
        self.report({'INFO'}, F'UVed at Angle Of : {self.angle_limit}')
        return {"FINISHED"}


    def parameter_getter(self):
        return self.rmargin


    def execute(self, context):

        self.og_active = context.active_object
        self.og_selection = context.selected_objects

        self.lazy_selection(context)

        if self.bweight_as_seams:
            for obj in bpy.context.selected_objects:
                bpy.context.view_layer.objects.active = obj
                me = obj.data
                #me.show_edge_crease = True

                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.mesh.select_mode(type="EDGE")
                selectSmoothEdges(self, me)
                bpy.ops.mesh.mark_seam(clear=False)
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.object.mode_set(mode='OBJECT')

        if self.rmethod:
            if bpy.app.version[1] <= 90:
                bpy.ops.uv.smart_project(angle_limit=self.angle_limit, island_margin=self.rmargin, user_area_weight=self.user_area_weight)
            
            elif bpy.app.version[1] > 90:
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.uv.smart_project(angle_limit=self.angle_limit, island_margin=self.rmargin, area_weight=self.user_area_weight, correct_aspect=False, scale_to_bounds=False)

        else:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=self.rmargin)
            bpy.ops.object.mode_set(mode='OBJECT')

        # Operator UI
        if HOPS_OT_XUnwrapF.called_ui == False:
            HOPS_OT_XUnwrapF.called_ui = True

            objs_unwrapped = len([obj for obj in context.selected_objects if obj.type == 'MESH'])

            ui = Master()
            ui.receive_draw_data(
                draw_data=[
                    ["Auto Unwrap"],
                    ["Unwrapped", objs_unwrapped],
                    ["Angle", self.angle_limit],
                    ["Weight", self.user_area_weight],
                    ["Margin", self.rmargin]])
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)

        # Call UV Draw op
        bpy.ops.hops.draw_uv_launcher(use_selected_meshes=True)

        self.set_selection_back(context)
        return {"FINISHED"}


    def lazy_selection(self, context):
        '''Make sure context selections are good.'''

        active = context.active_object
        mesh_objs = [obj for obj in context.selected_objects if obj.type == 'MESH']

        bpy.ops.object.select_all(action='DESELECT')

        for obj in mesh_objs:
            obj.select_set(True)

        context.view_layer.objects.active = active if active in mesh_objs else mesh_objs[0]


    def set_selection_back(self, context):
        '''Set the selection back to the original'''

        bpy.ops.object.select_all(action='DESELECT')
        context.view_layer.objects.active = self.og_active
        for obj in self.og_selection:
            obj.select_set(True)