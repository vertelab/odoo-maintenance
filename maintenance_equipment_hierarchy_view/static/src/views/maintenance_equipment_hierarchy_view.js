/** @odoo-module */

import { registry } from "@web/core/registry";
import { hierarchyView } from "@web_hierarchy/hierarchy_view";
import { HierarchyController } from "@web_hierarchy/hierarchy_controller";
import { MaintenanceEquipmentActionHelper } from "./maintenance_equipment_action_helper";
import { MaintenanceEquipmentHierarchyRenderer } from "./maintenance_equipment_hierarchy_renderer";

export class MaintenanceEquipmentHierarchyController extends HierarchyController {
    static template = "maintenance_equipment_hierarchy_view.HierarchyView";
    static components = { ...HierarchyController.components, MaintenanceEquipmentActionHelper };
}

export const maintenanceEquipmentHierarchyView = {
    ...hierarchyView,
    Controller: MaintenanceEquipmentHierarchyController,
    Renderer: MaintenanceEquipmentHierarchyRenderer,
};


registry.category("views").add("maintenance_equipment_hierarchy", maintenanceEquipmentHierarchyView);
