$(document).ready(function () {
    // Code adapted from http://djangosnippets.org/snippets/1389/  
    function updateElementIndex(el, prefix, ndx) {
        var id_regex = new RegExp('(' + prefix + '-\\d+-)');
        var replacement = prefix + '-' + ndx + '-';
        if ($(el).attr("for")) $(el).attr("for", $(el).attr("for").replace(id_regex,
        replacement));
        if (el.id) el.id = el.id.replace(id_regex, replacement);
        if (el.name) el.name = el.name.replace(id_regex, replacement);
    }

    function updateNumberDiagnosis() {
        $("#ul_diagnosis_formset ul:visible>li.number_diagnosis").each(function(index) {
            var text = "Диагноз #" + (index + 1);
            $(this).html(text);
        })
    }

    function deleteForm(btn, prefix) {
        var formCount = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
        var maxCount = parseInt($('#id_' + prefix + '-MAX_NUM_FORMS').val());
        var initialCount = parseInt($('#id_' + prefix + '-INITIAL_FORMS').val()) + 1
        if (formCount > 1) {
            var first_element = $("#ul_diagnosis_formset>ul:first")
            if (initialCount == formCount) {
                $(btn).parent().hide().filter("input,textarea").val("");
            } else {
                $(btn).parent().remove();
            }
            updateNumberDiagnosis();
            var forms = $('.diagnosis_form'); // Get all the forms  
            $('#id_' + prefix + '-TOTAL_FORMS').val(forms.length);
            var i = 0;
            for (formCount = forms.length; i < formCount; i++) {
                $(forms.get(i)).children(":visible").children().each(function () {
                    if ($(this).attr('type') == 'text') {
                        updateElementIndex(this, prefix, i);
                        updateNumberDiagnosis();
                    }
                });
            }
        } 
        else {
            alert("Нужно поставить пациенту диагноз!");
        }
        return false;
    }

    function show_tree_mkb(h_el) {
		$("#tree").dynatree({
			title: "Lazy loading sample",
			fx: { height: "toggle", duration: 200 },
			autoFocus: false, // Set focus to first child, when expanding or lazy-loading.
			initAjax: {
				url: "/mkb.json"
				},

			onActivate: function(node) {
                if (!node.data.isFolder) {
                    $('input[name$="code"]', h_el).val(node.data.code);
                    $('input[name$="name"]', h_el).val(node.data.name);
                    var text = node.data.name + ' ' + node.data.code;
                    $('li.diagnosis_content>span', h_el).text(text);
                    $('span.b-close').click();
                }
			},

			onLazyRead: function(node){
            	node.appendAjax({
            	    url: "/mkb.json",
		            data: {key: node.data.key,
            		       mode: "funnyMode"
                         }
                });
			}
		});
        $('#popup_mkb').bPopup({follow: [false, false],
                                width: 1024,
                                position: [0, $(h_el).offset().top + 50],
                                positionStyle: 'absolute'});
    }

    function addForm(btn, prefix) {
        var formCount = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
        var maxCount = parseInt($('#id_' + prefix + '-MAX_NUM_FORMS').val());
        var initialCount = parseInt($('#id_' + prefix + '-INITIAL_FORMS').val()) + 1
        if (formCount < maxCount) {
            var element = $("#ul_diagnosis_formset>ul:first").siblings().last().prev()
            var row = element.clone(false).get(0);
            $(row).removeAttr('id').hide().insertAfter(element).slideDown(300).click(function() {
                show_tree_mkb(this)
            });

            $(".errorlist", row).remove();
            $(row).children().removeClass("error");

            $(row).children().children().each(function () {
                updateElementIndex(this, prefix, formCount);
                if (this.type != "button") {
                    $(this).val("");
                }
                updateNumberDiagnosis();
            }).parent().find('span').text("Нет");

            $(row).find(".delete").click(function () {
                return deleteForm(this, prefix);
            });
            $("#id_" + prefix + "-TOTAL_FORMS").val(formCount + 1);
        } 
        else {
            alert("Больше диагнозов нельзя добавлять пациенту");
        }
        return false;
    }
    // Register the click event handlers
    $("#add").click(function () {
        return addForm(this, "diagnosis");
    });

    $(".delete").click(function () {
        return deleteForm(this, "diagnosis");
    });
    $('ul.diagnosis_form :button').click(function() {
        show_tree_mkb($(this).parents('ul.diagnosis_form'))
    });
    $("#diagnosis_form_0").siblings().each(function(index) {
        var element_id = $("#id_diagnosis-" + index +"-id");
        var value = element_id.val()
        if (value == "" || value == undefined) {
            element_id.parent().remove();
        } else {
            $("#li_diagnosis-" + index + "-delete").remove();
        }
    })

});
