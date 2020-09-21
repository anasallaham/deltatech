# ©  2015-2018 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import _, api, fields, models

from odoo.addons import decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_default_weight_uom_id(self):
        uom_kg = self.env.ref("product.product_uom_kgm")
        return uom_kg.id

    weight_uom = fields.Float(
        "Weight UoM",
        compute="_compute_weight_uom",
        digits=dp.get_precision("Stock Weight"),
        inverse="_set_weight_uom",
        store=True,
        help="The weight of the contents, not including any packaging, etc.",
    )

    weight_uom_id = fields.Many2one(
        "product.uom",
        "Weight UoM",
        default=_get_default_weight_uom_id,
        required=True,
        help="Default Unit of Measure used for weight.",
    )

    @api.depends("product_variant_ids", "product_variant_ids.weight")
    def _compute_weight(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.weight = template.product_variant_ids.weight
        for template in self - unique_variants:
            template.weight = 0.0

    @api.one
    def _set_weight(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.weight = self.weight

    @api.depends("product_variant_ids", "product_variant_ids.weight")
    def _compute_weight_uom(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.weight_uom = template.product_variant_ids.weight_uom
        for template in self - unique_variants:
            template.weight_uom = 0.0

    @api.one
    def _set_weight_uom(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.weight_uom = self.weight_uom

    @api.onchange("weight_uom", "weight_uom_id")
    def onchange_weight_uom(self):
        uom_kg = self.env.ref("product.product_uom_kgm")
        self.weight = self.weight_uom_id._compute_quantity(self.weight_uom, uom_kg)

    @api.model
    def create(self, vals):
        template = super(ProductTemplate, self).create(vals)
        # This is needed to set given values to first variant after creation
        related_vals = {}

        if vals.get("weight_uom"):
            related_vals["weight_uom"] = vals["weight_uom"]
        if vals.get("weight_uom_id"):
            related_vals["weight_uom_id"] = vals["weight_uom_id"]
        if related_vals:
            template.write(related_vals)
        return template


class ProductProduct(models.Model):
    _inherit = "product.product"

    weight_uom = fields.Float(
        "Weight UoM",
        digits=dp.get_precision("Stock Weight"),
        help="The weight of the contents, not including any packaging, etc.",
    )

    @api.onchange("weight_uom", "weight_uom_id")
    def onchange_weight_uom(self):
        uom_kg = self.env.ref("product.product_uom_kgm")
        self.weight = self.weight_uom_id._compute_quantity(self.weight_uom, uom_kg)
