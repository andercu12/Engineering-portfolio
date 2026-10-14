# src/materials.py

available_materials = [Al2O3, YSZ, NiCr]

COAT_MATERIALS = {
    "Al2O3" {
        density_g_cm3 3.95,
        base_efficiency 0.55
    },

    "YSZ" {
        density_g_cm3 6.0,
        base_efficiency 0.50
    },

    "NiCr" {
        density_g_cm3 8.2,
        base_efficiency 0.65
    }
}

def get_material_name(mat_idx):
    return available_materials[mat_idx-1]

def get_material(name):
    return COAT_MATERIALS[name]
