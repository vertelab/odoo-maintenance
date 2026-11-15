# odoo-maintenance — gren 19.0

> **Denna gren är avsiktligt tom.** Modulerna är INTE portade till Odoo 19.
> Grenen finns så att dev-miljöer (`hansolo19`) kan klona den utan att falla,
> men den påstår ingenting om att koden är portad.

## Baseline

| | |
|---|---|
| Källa | `20.0` |
| Moduler | **7** |
| Grenar i repot | `14.0`, `16.0`, `18.0`, `20.0`, `main` |

## Moduler

- `maintanance_request_ai`
- `maintenance_cve`
- `maintenance_equipment_hierarchy_view`
- `maintenance_equipment_monitoring`
- `maintenance_monitoring_status`
- `maintenance_monitoring_status_extension`
- `project_maintenance_customer_user_access`

## Blockerare

**1 externa beroenden saknas** i Odoo 19-kärnan och OCA 19.0:

| Beroende | Behövs av |
|---|---|
| `maintenance_equipment_hierarchy` | `maintenance_equipment_hierarchy_view` |

### Prioritering

Ett beroende som blockerar många moduler ger mest nytta att lösa först:

- `maintenance_equipment_hierarchy` — frisläpper **1** modul(er)

## Nästa steg

Portering sker på `*-pfile`-maskin med versionsagnostisk kod
(`.p.py` / `.p.xml`). Se `/skill:odoo-pfiles`.
