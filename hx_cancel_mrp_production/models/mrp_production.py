# -*- coding: utf-8 -*-
#############################################################################
#
#    HorizonX Technologies
#
#    Copyright (C) 2024-TODAY HorizonX Technologies (<https://www.thehorizonx.in>)
#    Author: Harshit Nariya (<https://www.thehorizonx.in>)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from collections import defaultdict

from odoo import models, _
from odoo.tools import float_round


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _prepare_move_vals_with_existing_move(self, move, factor, location_id=False, location_dest_id=False):
        location_id = location_id or move.location_dest_id
        location_dest_id = location_dest_id or move.location_id
        return {
            'name': move.name,
            'date': move.create_date,
            'product_id': move.product_id.id,
            'product_uom_qty': move.product_uom_qty * factor,
            'product_uom': move.product_uom.id,
            'procure_method': 'make_to_stock',
            'location_dest_id': location_dest_id.id,
            'location_id': location_id.id,
            'warehouse_id': location_dest_id.warehouse_id.id,
            'company_id': move.company_id.id,
        }

    def _create_move_with_existing_move(self, moves, factor, location_id=False, location_dest_id=False):
        move_vals = [self._prepare_move_vals_with_existing_move(move, factor, location_id, location_dest_id) for move in moves]
        return self.env['stock.move'].create(move_vals)

    def _prepare_move_line_vals_to_cancel(self, move, lot_id=False):
        val = {
            'move_id': move.id,
            'qty_done': move.product_uom_qty,
            'product_id': move.product_id.id,
            'product_uom_id': move.product_uom.id,
            'location_id': move.location_id.id,
            'location_dest_id': move.location_dest_id.id,
        }
        if lot_id:
            val.update({'lot_id': lot_id.id})
        return val

    def _create_move_line_vals_to_cancel(self, moves, lot_id=False):
        move_line_vals = [self._prepare_move_line_vals_to_cancel(move, lot_id) for move in moves]
        return self.env['stock.move.line'].create(move_line_vals)

    def action_cancel_mrp_production(self):
        factor = self.product_qty / self.product_uom_id._compute_quantity(self.product_qty, self.product_uom_id)

        def create_new_moves(moves, location_dest_id=None):
            return self._create_move_with_existing_move(moves, factor, location_dest_id=location_dest_id)

        # Filter done moves
        done_move_finished_ids = self.move_finished_ids.filtered(lambda l: l.state == 'done')
        done_move_raw_ids = self.move_raw_ids.filtered(lambda l: l.state == 'done')
        # Create new moves from existing ones
        new_move_finished_ids = create_new_moves(done_move_finished_ids)
        new_move_raw_ids = create_new_moves(done_move_raw_ids, location_dest_id=self.location_dest_id)

        all_new_moves = new_move_finished_ids + new_move_raw_ids
        if all_new_moves:
            all_new_moves._action_confirm()

        # Process finished moves
        done_finished_moves = new_move_finished_ids.filtered(lambda m: m.product_id == self.product_id)
        new_move_finished_ids -= done_finished_moves
        # Process tracking and non-tracking moves
        tracking_moves = done_move_finished_ids.filtered(lambda m: m.has_tracking != 'none')
        self._create_move_line_vals_to_cancel(tracking_moves)

        for move in done_move_finished_ids - tracking_moves:
            move.quantity_done = move.product_uom_qty

        qty_already_used = defaultdict(float)
        for move in new_move_raw_ids | new_move_finished_ids:
            if move.has_tracking != 'none':
                original_moves = self.move_raw_ids if move in new_move_raw_ids else self.move_finished_ids
                move_lines = original_moves.filtered(lambda m: m.product_id == move.product_id).mapped('move_line_ids')
                for move_line in move_lines:
                    available_qty = move_line.qty_done - qty_already_used[move_line]
                    taken_qty = min(move.product_uom_qty, available_qty)

                    if taken_qty > 0:
                        self._create_move_line_vals_to_cancel(move, lot_id=move_line.lot_id)
                        move.product_uom_qty -= taken_qty
                        qty_already_used[move_line] += taken_qty
            else:
                move.quantity_done = float_round(
                    move.product_uom_qty,
                    precision_rounding=move.product_uom.rounding)

        # Finalize the moves
        all_moves_to_finalize = done_finished_moves | new_move_finished_ids | new_move_raw_ids
        all_moves_to_finalize._action_done()

        # Link produced move lines to new finished moves
        produced_move_line_ids = new_move_raw_ids.mapped('move_line_ids').filtered(lambda ml: ml.qty_done > 0)
        new_move_finished_ids.mapped('move_line_ids').write({
            'produce_line_ids': [(6, 0, produced_move_line_ids.ids)]
        })

        # Cancel the original done moves and related records
        done_move_raw_ids.sudo().write({'state': 'cancel'})
        done_move_raw_ids.mapped('move_line_ids').sudo().write({'state': 'cancel'})

        # Cancel workorders if they exist
        if self.sudo().mapped('workorder_ids'):
            self.sudo().mapped('workorder_ids').write({'state': 'cancel'})

        # Cancel the production order
        self.write({'state': 'cancel'})
