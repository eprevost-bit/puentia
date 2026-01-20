from odoo import models, api, _, fields
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare


class AccountMove(models.Model):
    _inherit = 'account.move'

    def write(self, vals):
        # 1. Bypass de seguridad para administradores o procesos del sistema
        if self.env.is_superuser() or self.env.context.get('bypass_risk_check'):
            return super().write(vals)

        for move in self:
            if move.is_invoice(include_receipts=True):

                # 3. Verificamos el permiso
                if not self.env.user.has_group('sale_purchase_security.group_modify_posted_invoice'):

                    # 4. Lista de campos prohibidos
                    restricted_fields = {
                        'invoice_line_ids',  # Las líneas de factura
                        'line_ids',  # Las líneas contables (subyacentes)
                        'partner_id',  # El cliente/proveedor
                        'invoice_date',  # La fecha
                        'currency_id',  # La moneda
                        'invoice_payment_term_id'  # Plazos de pago
                    }

                    # 5. Comprobamos si intentan tocar algo prohibido
                    if any(field in vals for field in restricted_fields):
                        raise UserError(_(
                            "ACCESO DENEGADO.\n"
                            "No tienes permiso para modificar Facturas (en ningún estado).\n"
                            "Solicita el permiso 'Contabilidad: Modificar Facturas Publicadas' o contacta a tu administrador."
                        ))

        return super().write(vals)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.constrains('analytic_distribution')
    def _check_analytic_max_100(self):
        """
        Validar AL GUARDAR que no se pase del 100%.
        """
        for line in self:
            if line.analytic_distribution:
                # Sumamos los porcentajes
                total = sum(float(v) for v in line.analytic_distribution.values())

                # Si el total es MAYOR que 100.0 (float_compare devuelve 1)
                if float_compare(total, 100.0, precision_digits=2) == 1:
                    raise ValidationError(_(
                        "¡Error de Analítica en Línea de Factura!\n"
                        "Línea: %(label)s\n"
                        "Total asignado: %(sum)s%%\n\n"
                        "No puedes asignar más del 100%%. Ajusta los valores para guardar.",
                        label=line.name or line.product_id.name,
                        sum=total
                    ))