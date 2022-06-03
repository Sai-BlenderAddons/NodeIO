class BatchConvertor_preferences(bpy.types.AddonPreferences):
    bl_idname = get_addon_name()

    preferences_tabs =  [("GENERAL", "General", ""),
                        ("KEYMAPS", "Keymaps", ""),
                        ("ABOUT", "About", "")]
