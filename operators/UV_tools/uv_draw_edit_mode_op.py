import bpy

op_desc = '''Display the UVS
Click : Display selected face UVS
Shift : Display all UVS'''

class HOPS_OT_Draw_UV_Edit_Mode(bpy.types.Operator):
    bl_idname = "hops.draw_uv_edit_mode"
    bl_label = "UV Draw Edit Mode"
    bl_description = op_desc

    def invoke(self, context, event):
        
        mode = context.mode

        if event.shift:
            bpy.ops.hops.draw_uv_launcher(use_selected_meshes=True)
        else:
            bpy.ops.hops.draw_uv_launcher(use_selected_meshes=True, use_selected_faces=True)

        if mode == 'EDIT_MESH':
            if context.mode != 'EDIT_MESH':
                bpy.ops.object.mode_set(mode='EDIT')

        return {'FINISHED'}