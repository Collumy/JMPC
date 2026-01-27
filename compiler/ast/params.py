class SingularParameter:
    def __init__(self, name, slot, desc_slot, value_type, display_name=None, default=None):
        self.type_key = "singular"

        self.name = name
        self.slot = slot
        self.desc_slot = desc_slot
        self.display_name = display_name

        self.value_type = value_type
        self.default = default


class PluralParameter:
    def __init__(self, name, slots, desc_slots, value_type, ignore_empty = True, display_name=None, default=None):
        self.type_key = "plural"
        self.ignore_empty = ignore_empty

        self.name = name
        self.slots = slots
        self.desc_slots = desc_slots
        self.display_name = display_name

        self.value_type = value_type
        self.default = default



class EnumParameter:
    def __init__(self, name, slot, elements, default, display_name=None):
        self.type_key = "enum"

        self.elements = elements
        self.default = default

        self.name = name
        self.display_name = display_name
        self.slot = slot


class EnumElement:
    def __init__(self, name, display_name=None, icon=None):
        self.name = name
        self.display_name = display_name
        self.icon = icon