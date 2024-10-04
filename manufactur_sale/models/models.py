from odoo import models, fields, api
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def get_related_purchase_orders(self):
        purchase_orders = []
        for order in self:
            purchase_orders.extend(order._get_purchase_orders())
        return purchase_orders

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    child_mrp_production_ids = fields.One2many(
        comodel_name='mrp.production',
        compute='_compute_child_mrp_production_ids',
        string='Child Manufacturing Orders'
    )

    @api.depends('origin')
    def _compute_child_mrp_production_ids(self):
        for production in self:
            child_orders = self.env['mrp.production'].search([('origin', '=', production.name)])
            production.child_mrp_production_ids = child_orders

    move_more_child_ids = fields.One2many(
        comodel_name='mrp.production',
        compute='_compute_move_more_child_ids',
        string='All Child Manufacturing Orders'
    )

    @api.depends('origin')
    def _compute_move_more_child_ids(self):
        for production in self:
            production.move_more_child_ids = self._get_all_child_mrp_production_ids(production)

    def _get_all_child_mrp_production_ids(self, production):
        child_orders = self.env['mrp.production'].search([('origin', '=', production.name)])
        all_child_orders = child_orders
        for child in child_orders:
            all_child_orders |= self._get_all_child_mrp_production_ids(child)
        return all_child_orders
