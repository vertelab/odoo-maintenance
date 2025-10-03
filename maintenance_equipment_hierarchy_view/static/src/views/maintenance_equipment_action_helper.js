import { Component } from "@odoo/owl";

export class MaintenanceEquipmentActionHelper extends Component {
    static template = "maintenance_equipment_hierarchy_view.MaintenanceEquipmentActionHelper ";
    static props = { noContentTitle: { type: String }, noContentParagraph: { type: String } };
}
