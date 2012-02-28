//  Gestión de Trabajos Fin de Carrera de la Universidad de La Laguna
//
//    Copyright (C) 2011-2012 Pedro Cabrera <pdrcabrod@gmail.com>
//                            Jesús Torres  <jmtorres@ull.es>
//
//  This program is free software: you can redistribute it and/or modify
//  it under the terms of the GNU Affero General Public License as
//  published by the Free Software Foundation, either version 3 of the
//  License, or (at your option) any later version.
//
//  This program is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU Affero General Public License for more details.
//
//  You should have received a copy of the GNU Affero General Public License
//  along with this program.  If not, see <http://www.gnu.org/licenses/>.
//

var solicitud = {

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

        // Soporte para evitar que se tengan que reenviar los archivos
        $(selector).find("input:file").each(function() {
            var w = $(this);
            var idRegex = new RegExp("file$");
            idFileId = w.attr('id').replace(idRegex, 'fileid');
            idFilename = w.attr('id').replace(idRegex, 'filename');
            var fileid = $('#' + idFileId);
            if(fileid.val() != "") {
                w.hide();
                var file = $('<div></div>').insertBefore(w);
                file.append($('#' + idFilename).val());
                var change = '<input style="margin-left: 2em;" type="button" value="Cambiar"/>';
                $(change).appendTo(file).click(function() {
                    fileid.val('');
                    file.hide();
                    w.show(); w.focus(); w.click(); w.blur();
                });
            }
        });

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

function listado(resultsBox, searchBox, totalPages, options)
{
    // resultados continuos sin paginación
    var pagelessOptions = {
        totalPages: totalPages,
        url: './',
        params : {
            q: "{{ q }}"
        }
    }

    if ("pagelessLoaderMsg" in options) {
        pagelessOptions.loaderMsg = options['pagelessLoaderMsg'];
    }

    if ("pagelessLoaderImage" in options) {
        pagelessOptions.loaderImage = options['pagelessLoaderImage'];
    }

    $(resultsBox).pageless(pagelessOptions);

    // cuadro de búsqueda flotante
    $(searchBox).scrollToFixed({
        marginTop: -10,
        preFixed: function() {
            $(this).animate({"background-color": "#969"});
        },
        preUnfixed: function() {
            $(this).animate({"background-color": "#ffffff"});
        },
    });

    // autocompletado del cuadro de búsqueda
    $('#q', searchBox).autocomplete({
        source: function(request, response) {
            $.ajax({
                url: "./",
                dataType: "json",
                data: {
                    q: request.term,
                    json: 1,
                    per_page: 10,
                },
                success: function(data) {
                    response($.map(data, function(item) {
                        var results = {};
                        what = request.term.replace(' ', '|');
                        pattern = new RegExp('(' + what + ')','gi');
                        replaceWith = '<strong>$1</strong>';
                        return {
                            title: item.title.replace(pattern, replaceWith),
                            creator: item.creator.replace(pattern, replaceWith),
                            niu: item.niu.replace(pattern, replaceWith),
                            value: item.url.replace(pattern, replaceWith),
                        };
                    }));
                }
            });
        },
        minLength: 3,
        select: function(event, ui) {
            window.location.href = ui.item.value;
            return false;
        },
        focus: function(event, ui) {
            return false;
        }
    })
    .data("autocomplete")._renderItem = function(ul, item) {
        return $("<li></li>")
            .data("item.autocomplete", item)
            .append( "<a>" + item.title + "<br><small>" + item.creator +
                " (" + item.niu + ") " + "</small></a>" )
            .appendTo( ul );
    };

    // En caso de scroll cerrar el autocompletado para evitar problemas
    // visualizacion.
    $(window).scroll(function () {
        $('#q').autocomplete("close");
    });
}

function setupEditDialog(idPrefix, url)
{
    $('#' + idPrefix + '-editar').click(function() {
        // abrir el cuadro de diálogo
        var dialog = $('<div style="display:none" class="loading"></div>').appendTo('body');
        dialog.dialog({
            modal: true,
            resizable: false,
            width: 700,
            title: "Editar",
            buttons: {
                "Guardar": function() {
                    $(".ui-dialog :button").attr('disabled', 'disabled');
                    $(this).load(
                        url,
                        $('form', this).serializeArray(),
                        function (responseText, textStatus, XMLHttpRequest) {
                            var content = $('#' + idPrefix + '-wrapper', this);
                            if (content.length > 0) {
                                $($('#' + idPrefix + '-wrapper')[0]).replaceWith(content.clone());
                                setupEditDialog(idPrefix, url);
                                $(this).dialog("close");
                            }
                            else
                                $(".ui-dialog :button").removeAttr('disabled');
                        });
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
                $('.ui-dialog-buttonpane').find('button:contains("Guardar")').button({
                    icons: {primary: 'ui-icon-save'}
                });
                // para que ningún botón tenga el foco
                $(".ui-dialog :button").blur();
            },
            // añadimos un listener al cierre para evitar añadir múltiples divs al documento
            close: function(event, ui) {
                // remove div with all data and events
                dialog.remove();
            }
        });

        // cargamos el contenido remoto
        dialog.load(
            url,
            function (responseText, textStatus, XMLHttpRequest) {
                dialog.removeClass('loading');
            }
        );
        // evitar que el navegador siga el link
        return false;
    });
}