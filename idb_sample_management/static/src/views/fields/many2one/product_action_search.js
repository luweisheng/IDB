/** @odoo-module **/

import {patch} from "@web/core/utils/patch";
import { Many2XAutocomplete } from "@web/views/fields/relational_utils";

patch(Many2XAutocomplete.prototype, {
    async onSearchMore() {
        console.log('onSearchMore----------------------------');
        const result = await super.onSearchMore();
        if (result.dialogParams) {
            result.dialogParams.views.search = 'product_search_form_view202411191646';
            result.dialogParams.views.search_panel = {
                viewId: 'product_search_form_view202411191646',
                model: 'product.product',
                fields: ['categ_id', 'name'],
            };
        }
        debugger;
        return result;
    }
});