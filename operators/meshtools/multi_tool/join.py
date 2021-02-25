from .utils import *


class Join:
    def setup(self):
        self.start = False
        self.first_vert = None
        self.second_vert = None

        # Overrides
        self.override_release_confirm = False


    def update(self, context, event, data, op):
        # Cancel
        if event.type == 'C' and event.value == "PRESS":
            self.setup()

        # (1) First click : Get vert under mouse
        if self.start == False:
            if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                self.first_vert = get_vert_under_mouse(context, event, data)
                if self.first_vert != None:
                    self.start = True

        # (2) Mouse move : Show line to next vert under mouse
        if self.start == True:
            if event.type == "MOUSEMOVE":
                self.second_vert = get_vert_under_mouse(context, event, data)
                if self.first_vert == self.second_vert:
                    self.second_vert = None

        # (3) Second click : Join the (first vert, second vert) and start over
        if self.start == True:

            confirm = True if event.type == 'LEFTMOUSE' and event.value == 'PRESS' else False
            if self.override_release_confirm:
                confirm = True if event.type == 'LEFTMOUSE' and event.value == 'RELEASE' else confirm
                
            if confirm and self.first_vert and self.second_vert:
                verts = [self.first_vert, self.second_vert]
                bmesh.ops.connect_vert_pair(data.bm, verts=verts)
                self.setup()
                data.save()


    def help(self):
        return [
            ("C",     "Cancel selection"),
            ("Click", "Click 2 verts to join at last"),
            ("", "________JOIN________")]


    def draw_2d(self, context, data, op):
        pass


    def draw_3d(self, context, data, op):

        if self.first_vert != None:

            shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'POINTS', {'pos': [data.obj.matrix_world @ self.first_vert.co]})
            shader.bind()
            shader.uniform_float('color', (1,0,0,1))
            glEnable(GL_BLEND)
            glPointSize(6)
            batch.draw(shader)
            del shader
            del batch

        if self.second_vert != None:

            first_pos = data.obj.matrix_world @ self.first_vert.co
            second_pos = data.obj.matrix_world @ self.second_vert.co

            verts = [first_pos, second_pos]
            indices = [(0,1)]

            shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'LINES', {'pos': verts}, indices=indices)
            shader.bind()
            shader.uniform_float('color', (0,0,0,1))
            glEnable(GL_LINE_SMOOTH)
            glEnable(GL_BLEND)
            glLineWidth(3)
            batch.draw(shader)
            del shader
            del batch

        if self.first_vert != None and self.second_vert != None:

            shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'POINTS', {'pos': [data.obj.matrix_world @ self.second_vert.co]})
            shader.bind()
            shader.uniform_float('color', (1,0,0,1))
            glEnable(GL_BLEND)
            glPointSize(6)
            batch.draw(shader)
            del shader
            del batch
