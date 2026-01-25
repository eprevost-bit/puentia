from odoo import fields, models, api
from odoo.tools import SQL


class BudgetReport(models.Model):
    _inherit = 'budget.report'


    # -------------------------------------------------------------------------
    # NUEVO: CAMBIO DE NOMBRE EN FRONTEND (fields_get)
    # -------------------------------------------------------------------------
    @api.model
    def fields_get(self, allfields=None, attributes=None):
        """
        Sobrescribimos fields_get para interceptar la definición de los campos
        antes de enviarlos a la vista. Buscamos el campo que se llama
        'Distribución Analítica (1)' y le cambiamos el label a 'Areas'.
        """
        res = super().fields_get(allfields, attributes)

        # Recorremos los campos para encontrar el que tiene ese label específico
        for field_name, properties in res.items():
            # Verificamos si la propiedad 'string' (el nombre visible) coincide
            if properties.get('string') == 'Distribución Analítica (1)':
                # Cambiamos el nombre visible a 'Areas'
                properties['string'] = 'Areas'

                # Opcional: Si quieres asegurarte que salga ordenado o destacado,
                # puedes modificar otras propiedades aquí.
                break

        return res