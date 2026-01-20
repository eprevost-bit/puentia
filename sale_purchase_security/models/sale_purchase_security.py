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

    def button_confirm(self):
        """
        Validar que la distribución analítica sume 100% antes de confirmar.
        """
        self._check_analytic_distribution_100()
        return super().button_confirm()

    def _check_analytic_distribution_100(self):
        """
        Verifica línea por línea que, si tiene analítica, sume 100%.
        """
        for line in self.order_line:
            if line.display_type:
                continue  # Ignorar secciones y notas

            if line.analytic_distribution:
                # analytic_distribution es un diccionario {'id_cuenta': porcentaje}
                # Ejemplo: {'1': 50.0, '2': 50.0}

                total_percentage = sum(float(value) for value in line.analytic_distribution.values())

                # Usamos float_compare para evitar errores de redondeo (ej: 99.99999)
                # float_compare devuelve 0 si son iguales, -1 si es menor, 1 si es mayor
                comparison = float_compare(total_percentage, 100.0, precision_digits=2)

                if comparison != 0:
                    raise ValidationError(_(
                        "Error en la Distribución Analítica (Línea: %(product)s).\n"
                        "La suma de la distribución es %(total)s%%, pero debe ser EXACTAMENTE 100%%.\n"
                        "Por favor corrige la distribución.",
                        product=line.name,
                        total=total_percentage
                    ))