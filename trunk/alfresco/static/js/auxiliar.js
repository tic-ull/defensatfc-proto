//
// auxiliar.js - Funciones auxiliares
//

function configurarFormularioProyecto(form_selector, add_selector,
                                      remove_selector, numero_anexos)
{
        var anexo_counter = numero_anexos;

        var $tabs = $(form_selector).tabbed_formset({
            event: "mouseover",
            prefix: '{{ a.prefix }}',
            formTemplate: $("#anexo-empty-form"),
            tabTemplate: "<li><a href='#{href}'>#{label}</a> <span class='ui-icon ui-icon-close'>Eliminar anexo</span></li>",
            create: function(event, ui) {
                var select_on_create = 0;
                var tabs_nav = $(".ui-tabs-nav", this).children("li");

                var anchor = $(tabs_nav[0]).children("a");
                if ($(anchor.attr("href") + " .errorlist").length) {
                    anchor.toggleClass("errortab", true);
                }
                for (i = 1; i < tabs_nav.length; ++i) {
                    anchor = $(tabs_nav[i]).children("a");
                    if ($(anchor.attr("href") + " .errorlist").length) {
                        anchor.toggleClass("errortab", true);
                        if (select_on_create == 0) {
                            select_on_create = i;
                        }
                    }
                    anchor.text("Anexo " + i);
                    $(this).tabbed_formset("select", select_on_create);
                }
            }
        });

        // botón añadir anexo
        $(add_selector).button().click(function() {
            ++anexo_counter;
            var numero_anexos = $tabs.tabbed_formset("length");
            var tab_title = "Anexo " + numero_anexos;
            $tabs.tabbed_formset( "add", "#tabs-anexo-" + anexo_counter, tab_title );
        })

        // botón eliminar anexo
        $(remove_selector).live("click", function() {
            var index = $("li", $tabs).index( $( this ).parent() );
            var tabs = $(".ui-tabs-nav", $tabs).children("li");
            for (i = index + 1; i < tabs.length; ++i) {
                $(tabs[i]).children("a").text("Anexo " + (i - 1));
            }
            $tabs.tabbed_formset("remove", index);
        });
}