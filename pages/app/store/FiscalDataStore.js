/*
 * File: app/store/FiscalDataStore.js
 *
 * This file was generated by Sencha Architect version 2.1.0.
 * http://www.sencha.com/products/architect/
 *
 * This file requires use of the Ext JS 4.1.x library, under independent license.
 * License of Sencha Architect does not include license for Ext JS 4.1.x. For more
 * details see http://www.sencha.com/license or contact license@sencha.com.
 *
 * This file will be auto-generated each and everytime you save your project.
 *
 * Do NOT hand edit this file.
 */

Ext.define('MyApp.store.FiscalDataStore', {
    extend: 'Ext.data.Store',

    requires: [
        'MyApp.model.FiscalDataModel'
    ],

    constructor: function(cfg) {
        var me = this;
        cfg = cfg || {};
        me.callParent([Ext.apply({
            autoLoad: false,
            autoSync: false,
            storeId: 'fiscalDataStore',
            model: 'MyApp.model.FiscalDataModel',
            buffered: false,
            purgePageCount: 0,
            proxy: {
                type: 'ajax',
                api: {
                    //    create  : '/fiscal_data/create',
                    //    read    : '/fiscal_data/read',
                    //    update  : '/fiscal_data/update',
                    //    destroy : '/fiscal_data/destroy'
                },
                url: '/fiscal_data',
                reader: {
                    type: 'json'
                },
                writer: {
                    type: 'json',
                    allowSingle: false
                },
                listeners: {
                    exception: {
                        fn: me.onAjaxproxyException,
                        scope: me
                    }
                }
            }
        }, cfg)]);
    },

    onAjaxproxyException: function(server, response, operation, options) {
        alert ("Fiscal data Exception: "+ response);
    }

});