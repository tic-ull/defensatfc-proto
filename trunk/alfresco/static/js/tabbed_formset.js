//
// tabbed-formset.js - Formset dinámicos con JQuery tabs
// 
// Basado en:
// django-dynamic-formset
// 	Stanislaus Madueke (stan DOT madueke AT gmail DOT com)
//	http://code.google.com/p/django-dynamic-formset/
//
// djangosnippets
//	Dynamically adding forms to a formset with jQuery
//	http://djangosnippets.org/snippets/1389/
//
//   Copyright 2011 Jesús Torres <jmtorres@ull.es>
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//

(function($) {
    $.widget("ui.tabbed_formset", $.ui.tabs, {
	
	// Configuración por defecto del plugin
	options: {
            prefix: "",                         // El prefijo del formset de Django
            formTemplate: "#empty-form",        // Selector clonado para generar nuevos formularios
	},
	
	_create: function() {
            var w = this;

	    w.formTemplate = $(w.options.formTemplate);
            w.formTemplate.remove();

            var list = w.element.find("ol, ul").children("li:has(a[href])");
            list.each(function() {
                var href = $(this).find("a[href]").attr("href");
                w.element.find(href).each(function() {
                    w._hideDeleteCheckbox($(this));
                });
            });

            var prefix = w.options.prefix;
            w.formCounter = $("#id_" + prefix + "-TOTAL_FORMS").val();

            var addHandler = w.options.add;
            w.options.add = function(event, ui) {
                w._addHandler(event, ui, addHandler);
            };
            var removeHandler = w.options.remove;
            w.options.remove = function(event, ui) {
                w._removeHandler(event, ui, removeHandler);
            };

            $.ui.tabs.prototype._create.call(this);
        },

        _addHandler: function(event, ui, addHandler) {
            var prefix = this.options.prefix;
            var form = this.formTemplate.clone(true).removeAttr("id");
            this._updateFormIndexes(form, prefix, this.formCounter);
            this._hideDeleteCheckbox(form);
            $(ui.panel).append(form);
            $("#id_" + prefix + "-TOTAL_FORMS").val(++this.formCounter);
            if (addHandler !== null) { 
                addHandler.call(event, ui);
            }
        },

        _removeHandler: function(event, ui, removeHandler) {
            var form = $(ui.panel).children().clone(true).hide();
            var del = form.find('input:hidden[id $= "-DELETE"]');
            del.val("on");
            this.element.after(form);
            if (removeHandler !== null) {
                removeHandler.call(event, ui);
            }
        },

        _hideDeleteCheckbox: function(form) {
            // Ocultar los checkbox DELETE
            var del = form.find('input:checkbox[id $= "-DELETE"]');
            if (del.is(":checked")) {
                // Si un formset contiene un formulario borrado, hay que
                // mantenerlo oculto y evitar que se cree un tab para el mismo
                var hideForm = form.clone(true).hide();

                del = hideForm.find('input:checkbox[id $= "-DELETE"]');
                del.before('<input type="hidden" name="' + del.attr('name') +
                    '" id="' + del.attr('id') +'" value="on" />');
                this.element.after(hideForm);

                this.element.find("ol, ul").children("li:has(a[href='#" +
                    form.attr("id") +"'])").remove();
                form.remove();
            }
            else {
                del.before('<input type="hidden" name="' + del.attr('name') +
                    '" id="' + del.attr('id') +'" />');
                // Ocultar cualquier etiqueta asociada con el checkbox DELETE
                form.find('label[for="' + del.attr("id") + '"]').hide();
            }
            del.remove();
        },

        _updateElementIndex: function(element, prefix, index) {
            var idRegex = new RegExp(prefix + "-__prefix__-");
            var replacement = prefix + '-' + index + '-';
            if (element.attr("for"))
                element.attr("for", element.attr("for").replace(idRegex, replacement));
            if (element.attr('id'))
                element.attr('id', element.attr('id').replace(idRegex, replacement));
            if (element.attr('name'))
                element.attr('name', element.attr('name').replace(idRegex, replacement));
        },

        _updateFormIndexes: function(form, prefix, index) {
            var childElementSelector = 'input,select,textarea,label,div';
            var w = this;
            form.find(childElementSelector).each(function() {
                w._updateElementIndex($(this), prefix, index);
            });
        }
     });
})(jQuery);