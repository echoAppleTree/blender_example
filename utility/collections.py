import bpy
from .. preferences import get_preferences


def unlink_obj(context, obj):
    for coll in context.scene.collection.children:
        for ob in bpy.data.collections[coll.name].objects:
            if obj == bpy.data.collections[coll.name].objects[ob.name]:
                bpy.data.collections[coll.name].objects.unlink(obj)


def link_obj(context, obj, name="Cutters"):
    if name not in bpy.data.collections:
        new_col = bpy.data.collections.new(name='Cutters')
        if hasattr(new_col, 'color_tag'):
            new_col.color_tag = get_preferences().color.colection_color
        context.scene.collection.children.link(new_col)

    bpy.data.collections[name].objects.link(obj)


def find_collection(context, item):
    collections = item.users_collection
    if len(collections) > 0:
        return collections[0]
    return context.scene.collections


def hide_all_objects_in_collection(coll):
    '''Hide all objects in the collection passed in.'''

    for obj in coll.objects:
        if hasattr(obj, 'hide_set'):
            obj.hide_set(True)


def turn_on_parent_collections(obj, start_coll):
    '''Recursively turn on all parent collections that the object is in.'''

    for child in start_coll.children:
        if type(child) == bpy.types.Collection:
            turn_on_parent_collections(obj, child)
            if obj.name in child.objects:
                view_layer_unhide(child, enable=True)
                return True
    return False


def view_layer_unhide(collection, check=None, chain=[], enable=False):
    '''Recursively unhide collections until reaching passed in collection.'''

    view_layer_collection = bpy.context.view_layer.layer_collection
    current = view_layer_collection if not check else check

    if collection.name in current.children:
        collection.hide_viewport = False

        collection = current.children[collection.name]
        collection.hide_viewport = False

        if enable:
            collection.exclude = False

        for col in chain:
            col.hide_viewport = False
            bpy.data.collections[col.name].hide_viewport = False

            if enable:
                col.exclude = False

        return True

    for child in current.children:
        if not child.children:
            continue

        if check:
            chain.append(check)

        if view_layer_unhide(collection, check=child, chain=chain, enable=enable):
            child.hide_viewport = False
            bpy.data.collections[child.name].hide_viewport = False

            if enable:
                child.exclude = False

            return True

    return False
