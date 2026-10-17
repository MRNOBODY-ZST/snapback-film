# SnapBack licensing and third-party notices

Original SnapBack firmware, tools, parameter records, mechanical/electronic design source, independently designed bench exports and documentation are licensed under the root [MIT License](LICENSE). This includes the original code under `firmware/src`, `firmware/tests`, `firmware/host`, `tools`, and the independent `cad/feed_test_rig/R0_bench` and `cad/roller_test_rig/R0_bench` designs.

The following reference assets are **exceptions to MIT**. Their original authors retain their rights. No endorsement by those authors, Fujifilm, Mamiya or another camera manufacturer is implied. Reference geometry is not a manufacturing-qualified SnapBack camera interface.

| Paths | Author / upstream | Applicable license and attribution |
|---|---|---|
| `cad/reference/g_adapter_v2/` | rodgsilva / rodsgear; upstream moebot3000 | [CC BY 4.0](LICENSES/CC-BY-4.0.txt); [original attribution and source](cad/reference/g_adapter_v2/ATTRIBUTION.md) |
| `cad/reference/g_adapter_v4/` | SPRKPLG / Thnikkamax; upstream rodgsilva / rodsgear | [CC BY 4.0](LICENSES/CC-BY-4.0.txt); [original attribution and source](cad/reference/g_adapter_v4/ATTRIBUTION.md) |
| `cad/reference/square_pressure_cc0/` | SPRKPLG / Thnikkamax | [CC0 1.0](LICENSES/CC0-1.0.txt); [source notice](cad/reference/square_pressure_cc0/ATTRIBUTION.md) |
| `cad/reference/square_cartridge_lgpl/` original STL, README and license notice | Jocelyn Girard / jclngrrd | GNU LGPL 2.1 as linked by the original author; [license text](LICENSES/LGPL-2.1-only.txt), accompanying [GPL 2.0 text](LICENSES/GPL-2.0-only.txt), [original attribution](cad/reference/square_cartridge_lgpl/ATTRIBUTION.md) |
| `cad/cartridge/R0_reference_only/instax_square_cartridge.SOURCE_REFERENCE.step` and `.stl` | Derived from Jocelyn Girard's reference mesh | LGPL 2.1 reference geometry, **not MIT**; [conversion/change notice](cad/cartridge/R0_reference_only/README.md) |
| `cad/reference/super67/` original CAD and README | Damien A.W. Humby / DamienHazard; original upstream credits retained | [CC BY-NC-SA 4.0](LICENSES/CC-BY-NC-SA-4.0.txt); [attribution, pinned commit and comparison-only scope](cad/reference/super67/ATTRIBUTION.md) |

The Super-67 files are included as separately licensed, unchanged, noncommercial research references. They are not sources of copied geometry for SnapBack's original MIT bench designs; MIT does not grant commercial reuse of these NC reference files. Reuse them only under their own license. The same distinction applies to LGPL source geometry and its reference preview: distributing it beside MIT code does not relicense the geometry.

Original asset authors, URLs, license identifiers, modification flags and SHA-256 hashes are recorded in [cad/reference/source-manifest.json](cad/reference/source-manifest.json). License texts were archived without modification from the licensing organizations/SPDX; their sources and hashes are in [LICENSES/source-manifest.json](LICENSES/source-manifest.json). The original author notices remain unchanged.

The conversion script [instax_square_cartridge.py](cad/source/instax_square_cartridge.py) is original MIT code; the source mesh and resulting preview retain the separately stated geometry license. Reproduction of the preview can use the included original mesh, explicit transform configuration and conversion source. No original analytic CAD source is claimed for that third-party mesh.

External manuals, patents, product drawings, photographs, linked websites, installed development dependencies and third-party software retain their own terms. References to those materials do not grant a patent/trademark license or incorporate them into SnapBack's original design license. This repository does not distribute its local dependency runtime or a final camera-back product.
