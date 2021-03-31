'''
Copyright (C) 2021 Jean Da Costa Machado
blendeto@gmail.com

Created by Jean Da Costa Machado

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

import math
import bpy


bl_info = {
    'name': 'Pressure simulation',
    'description': 'Creates strength feedback based on mouse speed',
    'author': 'Jean Da Costa Machado',
    'version': (0, 0, 1),
    'blender': (2, 92, 0),
    'location': 'View3D > Sculpt Mode > Tools > Pressure Simulation',
    'warning': 'This addon is still in development.',
    'wiki_url': '',
    'category': 'Sculpt'}


# ---------------------------------------    Main Class   ------------------
class PresssureSim(bpy.types.Operator):
    bl_idname = 'ops.pressure_simulate'
    bl_label = 'simulate pressure'
    _timer = None


    lmx = 0
    lmy = 0
    samples = []
    sample_change_test = None

    def modal(self, context, event):
        # if false, stop
        if context.scene.pressure_sim_enable == False:
            return self.cancel(context)

        if event.type == 'TIMER' and context.object.mode == 'SCULPT':

            # get props from context.Scene
            sample_amount = context.scene.pressure_sim_sample_rate
            subtract = context.scene.pressure_sim_subtract
            atenuate = context.scene.pressure_sim_atenuation
            max_val = context.scene.pressure_sim_max
            min_val = context.scene.pressure_sim_min
            fallof = context.scene.pressure_sim_fallof

            # coordinates
            mx = event.mouse_x
            my = event.mouse_y
            lmx = self.lmx
            lmy = self.lmy

            # delta
            dx = mx - lmx
            dy = my - lmy
            # magnitude
            m = math.sqrt(dx * dx + dy * dy)

            # interpolate multiples samples
            self.samples.append(m)
            while len(self.samples) > sample_amount:
                del self.samples[0]

            mix = max(sum(self.samples) / len(self.samples) / atenuate - subtract, 0)
            mix **= fallof
            mix = (max(min(mix, max_val), min_val))

            # paint settings

            ps = context.scene.tool_settings.unified_paint_settings
            if ps.use_unified_strength:
                ps.strength = mix
            else:
                context.tool_settings.sculpt.brush.strength = mix

            # check sample_amount change and clear samples
            if self.sample_change_test != sample_amount:
                self.samples = []

            # last coordinates and sample_amount change test
            self.lmx = mx
            self.lmy = my
            self.sample_change_test = sample_amount
        return {'PASS_THROUGH'}

    def execute(self, context):
        if not context.scene.pressure_sim_enable:
            # toggle on
            wm = context.window_manager
            self._timer = wm.event_timer_add(1/60, window=context.window)
            wm.modal_handler_add(self)
            context.scene.pressure_sim_enable = True

            return {'RUNNING_MODAL'}
        else:
            # toggle off
            context.scene.pressure_sim_enable = False
            return {'CANCELLED'}

    def invoke(self, context, event):
        return self.execute(context)

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        return {'CANCELLED'}


# --------------------------------------------------  draw Panel
class PressureSimPannel(bpy.types.Panel):
    bl_category = 'Tool'
    bl_context = '.sculpt_mode'
    bl_label = 'Pressure SImulate'
    bl_region_type = 'UI'
    bl_space_type = 'VIEW_3D'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        if not context.scene.pressure_sim_enable:
            ps = layout.operator('ops.pressure_simulate', text='start pressure simulation')
        else:
            ps = layout.operator('ops.pressure_simulate', text='stop pressure simulation')
        layout.prop(context.scene, 'pressure_sim_sample_rate')
        layout.prop(context.scene, 'pressure_sim_atenuation')
        layout.prop(context.scene, 'pressure_sim_subtract')
        layout.prop(context.scene, 'pressure_sim_max')
        layout.prop(context.scene, 'pressure_sim_min')
        layout.prop(context.scene, 'pressure_sim_fallof')


# -----------------------------------------------------    register \ unregister
def register():
    bpy.utils.register_class(PresssureSim)
    bpy.utils.register_class(PressureSimPannel)

    bpy.types.Scene.pressure_sim_enable = bpy.props.BoolProperty(
        name='pressure_sim_enable',
        default=False)

    bpy.types.Scene.pressure_sim_sample_rate = bpy.props.IntProperty(
        name='samples',
        default=30,
        min=1)

    bpy.types.Scene.pressure_sim_subtract = bpy.props.FloatProperty(
        name='subtract',
        default=0.0)

    bpy.types.Scene.pressure_sim_atenuation = bpy.props.FloatProperty(
        name='atenuate',
        default=250)

    bpy.types.Scene.pressure_sim_min = bpy.props.FloatProperty(
        name='min',
        default=0.1,
        max=1)

    bpy.types.Scene.pressure_sim_max = bpy.props.FloatProperty(
        name='max',
        default=1.0,
        min=0)


    bpy.types.Scene.pressure_sim_fallof = bpy.props.FloatProperty(
        name='fallof',
        default=0.5,
        min=0.01,
        max=5)


def unregister():
    bpy.utils.unregister_class(PresssureSim)
    bpy.utils.unregister_class(PressureSimPannel)
    del bpy.types.Scene.pressure_sim_enable
    del bpy.types.Scene.pressure_sim_sample_rate
    del bpy.types.Scene.pressure_sim_subtract
    del bpy.types.Scene.pressure_sim_atenuation
    del bpy.types.Scene.pressure_sim_max
    del bpy.types.Scene.pressure_sim_min
    del bpy.types.Scene.pressure_sim_fallof


if __name__ == '__main__':
    register()
