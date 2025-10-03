/** @odoo-module **/

import { Avatar } from "@mail/views/web/fields/avatar/avatar";

import { HierarchyRenderer } from "@web_hierarchy/hierarchy_renderer";
import { MaintenanceEquipmentHierarchyCard } from "./maintenance_equipment_hierarchy_card";

export class MaintenanceEquipmentHierarchyRenderer extends HierarchyRenderer {
    static template = "maintenance_equipment_hierarchy_view.MaintenanceEquipmentHierarchyRenderer";
    static components = {
        ...HierarchyRenderer.components,
        HierarchyCard: MaintenanceEquipmentHierarchyCard,
        Avatar,
    };
}
