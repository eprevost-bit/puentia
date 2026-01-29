from odoo import models, api, _, fields
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare


class AccountMove(models.Model):
    _inherit = 'account.move'

    def write(self, vals):
        # 1. Bypass para administradores
        if self.env.is_superuser() or self.env.context.get('bypass_risk_check'):
            return super().write(vals)

        for move in self:
            if move.state == 'posted' and move.is_invoice(include_receipts=True):

                if not self.env.user.has_group('sale_purchase_security.group_modify_posted_invoice'):
                    restricted_fields = {
                        'invoice_line_ids', 'line_ids', 'partner_id',
                        'invoice_date', 'currency_id', 'invoice_payment_term_id'
                    }
                    if any(field in vals for field in restricted_fields):
                        raise UserError(_(
                            "ACCESO DENEGADO.\n"
                            "No tienes permiso para modificar una Factura ya Publicada.\n"
                            "Solicita el permiso especial o reviértela a borrador si es permitido."
                        ))

        return super().write(vals)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def write(self, vals):
        if self.env.is_superuser() or self.env.context.get('bypass_risk_check'):
            return super().write(vals)

        # Campos financieros críticos
        financial_fields = {'price_unit', 'discount', 'quantity'}

        # Si el usuario intenta cambiar precio, descuento o cantidad...
        if any(field in vals for field in financial_fields):
            for line in self:
                # 1. Comprobamos si viene de una VENTA (sale_line_ids tiene valor)
                # 2. Comprobamos si viene de una COMPRA (purchase_line_id tiene valor)
                is_from_sale = bool(line.sale_line_ids)
                is_from_purchase = bool(line.purchase_line_id)

                if is_from_sale or is_from_purchase:
                    # Opcional: Permitir al grupo especial modificar precios incluso si vienen de venta/compra
                    # Si quieres que NADIE pueda cambiarlo, borra las siguientes 2 líneas.
                    if self.env.user.has_group('sale_purchase_security.group_modify_posted_invoice'):
                        continue

                    origin_type = "Pedido de Venta" if is_from_sale else "Pedido de Compra"
                    raise UserError(_(
                        "OPERACIÓN BLOQUEADA.\n"
                        "Esta línea proviene de un %(origin)s.\n"
                        "No puedes cambiar el precio, cantidad o descuento directamente en la factura.\n"
                        "Debes corregir el pedido original si es necesario.",
                        origin=origin_type
                    ))

        return super().write(vals)

    @api.constrains('analytic_distribution')
    def _check_analytic_exact_100(self):
        """
        Validación Analítica: Exige que sea EXACTAMENTE 100%.
        Si es 99% o 101%, lanzará error.
        """
        for line in self:
            if line.analytic_distribution:
                total = sum(float(v) for v in line.analytic_distribution.values())
                if float_compare(total, 100.0, precision_digits=2) != 0:
                    raise ValidationError(_(
                        "¡Error de Analítica!\n"
                        "Producto: %(prod)s\n"
                        "La distribución suma actualmente un %(sum)s%%.\n"
                        "Es obligatorio que la suma sea EXACTAMENTE 100%%.",
                        prod=line.name or line.product_id.name or 'Línea sin nombre',
                        sum=total
                    ))