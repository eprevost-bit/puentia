from odoo import models, api, _, fields
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def write(self, vals):
        # Permitir si es superusuario o proceso del sistema
        if self.env.is_superuser() or self.env.context.get('bypass_risk_check'):
            return super().write(vals)

        for order in self:
            # Estado 'sale' es confirmado, 'done' es bloqueado
            if order.state in ['sale']:
                if not self.env.user.has_group('sale_purchase_security.group_modify_confirmed_sale'):
                    # Campos sensibles que no se deben tocar
                    restricted_fields = {'partner_id', 'order_line', 'pricelist_id', 'date_order', 'payment_term_id'}

                    if any(field in vals for field in restricted_fields):
                        raise UserError(_(
                            "No tienes permiso para modificar un Pedido de Venta confirmado.\n"
                            "Solicita el permiso 'Ventas: Modificar Pedidos Confirmados'."
                        ))
        return super().write(vals)

    def action_confirm(self):
        """Validar analítica al confirmar venta"""
        self._check_analytic_distribution_100()
        return super().action_confirm()

    def _check_analytic_distribution_100(self):
        for line in self.order_line:
            if line.display_type: continue

            if line.analytic_distribution:
                total = sum(float(v) for v in line.analytic_distribution.values())
                if float_compare(total, 100.0, precision_digits=2) != 0:
                    raise ValidationError(_(
                        "Error Analítico en Ventas (Producto: %(prod)s).\n"
                        "La suma es %(sum)s%%, DEBE ser exactamente 100%%.",
                        prod=line.name, sum=total
                    ))