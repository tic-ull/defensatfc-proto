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

var listado = {

    init: function(resultsBox, searchBox, totalPages, options) {

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
};
