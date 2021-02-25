from ... import bl_info
from ... preferences import get_preferences

'''
Make sure to have 2 or more items per list item.
'''


# Screen Saver Tips
tips = [
    ["Sharpen / Csharp", "Ctrl + click to apply booleans!", "Also performs sharpening", "Part of sharpen"],
    ["Settings >> Shade Solid", "Shift + Click to duplicate and make solid", "Read the tooltip"],
    ["BoolShift", "Select a boolshape and press Q", "Shift a bool to any state from any state."],
    ["To_Shape V2", "Q >> O >> T ", "Quick access w/to_shape V2", "Allows for the creation of a shape in the area of a selection", "Decap allows for various interesting possibities"],
    ["Q >> Add Modifiers >> Cloth", "Convert a selection to cloth", "Adjust pressure in the cloth panel", "Adjust the shrinkage amount as well.", "Optimized for single sided geometry"],
    ["Spherecast", "Q >> Meshtools >> Spherecast", "Converts a box into a sphere.","Adds a subdivision then cast modifier."],
    ["Bevel", "1 - Resets bevel to edge bevel defaults (profile 0.5)", "2 - Sets bevel to vert bevel defaults (profile 0.5)", "3 - Allows for a profile 1.0 bevel w/ edge. Useful for subdivision conversion"],
    ["Array V2", "Press V for 3d array", "Allows for a more interactive way to set the distance and segments at once."],
    ["LookDev +", "Alt + V >> V", "Press R in modal to set the environment to the render."],
    ["Subdivison", "Q >> Add Modifier >> Subdivision", "Alt + Click to set it first in the stack", "Can be assistive with upresing boolean geometry."],
    ["Taper", "Q >> Meshtools >> Taper", "Shift + clicking allows for individual tapering of multiple objects.", "Useful for tapering boolshapes post boxcutting"],
    ["Dice", "Ctrl + Click to dice on all axis'", "Alt + click to smart apply unto dice.","Pressing T allows for Twist to be used post dice"],
    ["Stacking Bevels", "Ctrl + click to add a 30 degree bevel ", "Ctrl + shift click to add a 60 degree bevel", "Q >> Operations >> Step will also add a 60 degree bevel in non-destructive mode."],
    ["Smart Shapes", "Activate Hopstool using the T Panel button", "The topbar has a plethora of smart shapes to choose from", "Hold ctrl to view dots and adjust shapes dynamically."],
    ["Manage", "Unify - bring all solid objects into the active collection", "Sync - ensure render settings are the exact same as viewport", "Evict - remove cutters and evict cutters to the Cutters collection", "Collect - Unify all solid objects into a reusable collection prime for reuse with PowerLink!"],
    ["Smooth", "Shift + click to create a smart vgroup for omission", "Allows for mirrored smoothing", "Ideal for hard surface smoothing"],
    ["New Modifier", "Ctrl + click any modifier to add a new modifier", ],
    ["UV Display", "Q >> O >> U", "Display UVs on the fly. In the 3d view!", "Auto UV under Q >> Meshtools >> Auto UV also displays UVs"],
    ["Mark ", "Edit Mode Q >> Mark", "Without selection mark performs an ssharpen operation "],
    ["Cloth ", "First button use adds modifiers and sets up smart group ", "Second use activates a modal allowing for settings to be adjusted on the fly "],
    ["Up to date? ", "The hops button at the top of the 3d view will tell you ", "Icons are also available for the marketplace of your choosing ","Get updated!"],
    ["Accushape ", "Located in Q >> Operations", "Also at the top of hopstool >> Alt + W ", "Allows for interactive scaling and proportion adjustments of objects"],
    ["Radial Array ", "For single axis mirroring you use mirror (alt + X)", "For radial mirroring, radial array is recommended "],
    ["Sculpt Quick Jump ", "Q >> Operations >> Brush ", "Displays a brush window for quick selection ", "Now supports cloth filter"],
    ["Multi Axial Dice ", "Q >> Meshtools >> Dice (ctrl + click)", "Ctrl + clicking Dice will dice on all axis ", "Dice can be used as a remesher of sorts this way"],
    ["UV Display ", "Q >> O >> U ", "Displays uvs in the 3d view. "],
    ["Pizza", "Ever order a pizza?", "Q >> Settings >> Pizza Ops", "AR hates it but it's a classic"],
    [f"HardOPS Version: {bl_info['version'][0]}.{bl_info['version'][1]}.{bl_info['version'][2]}.{bl_info['version'][3]}", f"Service Pack Level: {bl_info['version'][3]}"],
    ["Tips V1", "This is still a concept", "Thanks for reading my tips"],
    ["Boolean Grates", "HOPStool grid shapes can be shift clicked to conform to a boolshape", "Try it out!"],
    ["",""]
]
