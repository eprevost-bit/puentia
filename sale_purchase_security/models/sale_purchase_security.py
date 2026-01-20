from odoo import models, api, _, fields
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def write(self, vals):
        """
        Restringir la edición de pedidos confirmados solo a usuarios autorizados.
        """
        # Si el usuario es Superusuario (OdooBot) o estamos haciendo operaciones del sistema, permitimos.
        if self.env.is_superuser() or self.env.context.get('bypass_risk_check'):
            return super().write(vals)

        # Verificamos si se intenta escribir en pedidos ya confirmados
        for order in self:
            if order.state in ['purchase', 'done']:
                # Verificamos si el usuario pertenece al grupo autorizado
                if not self.env.user.has_group('sale_purchase_security.group_modify_confirmed_purchase'):
                    # Lista de campos que SÍ se permite tocar (por ejemplo, mensajes del chatter)
                    # Si 'vals' trae algo que no sea tracking o log, bloqueamos.
                    # Nota: A veces Odoo escribe campos técnicos, así que validamos campos "importantes".
                    restricted_fields = {'partner_id', 'order_line', 'currency_id', 'date_order'}

                    if any(field in vals for field in restricted_fields):
                        raise UserError(_(
                            "No tienes permiso para modificar un pedido confirmado.\n"
                            "Contacta a un administrador o solicita que te asignen al grupo 'Modificar Pedidos Confirmados'."
                        ))

        return super().write(vals)

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.constrains('analytic_distribution')
    def _check_analytic_max_100(self):
        for line in self:
            if line.analytic_distribution:
                total = sum(float(v) for v in line.analytic_distribution.values())
                if float_compare(total, 100.0, precision_digits=2) == 1:
                    raise ValidationError(_(
                        "¡Error de Analítica en Compra!\n"
                        "Producto: %(prod)s\n"
                        "Total asignado: %(sum)s%%\n"
                        "No puedes superar el 100%%.",
                        prod=line.name,
                        sum=total
                    ))