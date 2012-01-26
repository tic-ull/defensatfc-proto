//
// proyecto.js - Funciones auxiliares
//

var proyecto = {

    initForm: function(selector, options) {
        var prefix = "";
        var anexo_counter = 0;
        var formTemplate = "#empty-form";

        if ("anexoFormsetPrefix" in options) {
            prefix = options['anexoFormsetPrefix'];
        }

        if ("anexoNo" in options) {
            anexo_counter = options['anexoNo'] - 1;
        }

        if ("anexoFormTemplate" in options) {
            formTemplate = options['anexoFormTemplate'];
        }

        var $tabs = $(selector).tabbed_formset({
            prefix: prefix,
            formTemplate: formTemplate,
            tabTemplate: "<li><a href='#{href}'>#{label}</a> <span class='ui-icon ui-icon-close'>Eliminar anexo</span></li>",
            create: function(event, ui) {
                var select_on_create = -1;
                var tabs_nav = $(".ui-tabs-nav", this).children("li");

                for (i = 0; i < tabs_nav.length; ++i) {
                    var anchor = $(tabs_nav[i]).children("a");
                    if ($(anchor.attr("href") + " .errorlist").length) {
                        anchor.toggleClass("errortab", true);
                        if (select_on_create == -1) {
                            select_on_create = i;
                        }
                    }
                    if (anchor.filter("[href^=#tabs-" + prefix + "]").length) {
                        anchor.text("Anexo" + i);
                    }
                }
                $(this).tabbed_formset("select", select_on_create);
            }
        });

        // botón añadir anexo
        if ("anexoAddButton" in options) {
            $(options['anexoAddButton']).button().click(function() {
                ++anexo_counter;
                var anexos_no = $tabs.tabbed_formset("length");
                var tab_title = "Anexo " + anexos_no;
                $tabs.tabbed_formset("add",
                    "#tabs-" + prefix + "-" + anexo_counter, tab_title );
            });
        }

        // botón eliminar anexo
        if ("anexoRemoveButton" in options) {
            $(options['anexoRemoveButton']).live("click", function() {
                var selected = $tabs.tabbed_formset("option", "selected");
                var to_remove = $("li", $tabs).index($(this).parent());
                $tabs.tabbed_formset("select", to_remove);

                var dialog = "<div>"
                dialog += '<span class="icon-warning"></span>';
                dialog += "<p style='margin-left: 39px;'>¿Está seguro de que desea eliminar el ";
                dialog += $(this).prev("a").text();
                dialog += " y toda la información guardada en el formulario? ";
                dialog += "Tenga en cuenta que una vez borrada no será posible recuperarla.</p></div>"
                
                var div = $(dialog);
                div.attr("title","Confirmar").appendTo("body").dialog({
                    modal: true,
                    resizable: false,
                    buttons: {
                        "Aceptar": function() {
                            var tabs = $(".ui-tabs-nav", $tabs).children("li");
                            for (i = to_remove + 1; i < tabs.length; ++i) {
                                $(tabs[i]).children("a").text("Anexo " + (i - 1));
                            }
                            $tabs.tabbed_formset("select", selected);
                            $tabs.tabbed_formset("remove", to_remove);
                            $(this).dialog("close");
                        },                        
                        "Cancelar": function() {
                            $(this).dialog("close");
                        }
                    },
                    open: function() {
                        // para que los botones tenga iconos
                        $('.ui-dialog-buttonpane').find('button:contains("Cancelar")').button({
                            icons: {primary: 'ui-icon-close'}
                        });
                        $('.ui-dialog-buttonpane').find('button:contains("Aceptar")').button({
                            icons: {primary: 'ui-icon-check'}
                        });
                        // para que ningún botón tenga el foco
                        $(".ui-dialog :button").blur();
                    },
                    close: function() {
                        div.remove();
                    }
                });
            });
        }
    }
};