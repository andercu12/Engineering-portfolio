"""Illustrative material properties, not calibrated process data."""
available_materials = ['Al2O3', 'YSZ', 'NiCr']
COAT_MATERIALS = {
    'Al2O3': {'density_g_cm3': 3.95, 'base_efficiency': 0.55},
    'YSZ': {'density_g_cm3': 6.0, 'base_efficiency': 0.50},
    'NiCr': {'density_g_cm3': 8.2, 'base_efficiency': 0.65},
}


def get_material_name(mat_idx):
    if mat_idx not in range(1, len(available_materials) + 1):
        raise ValueError('Select a material from 1 to 3.')
    return available_materials[mat_idx - 1]


def get_material(name):
    return COAT_MATERIALS[name].copy()
