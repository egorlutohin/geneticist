$(document).ready(function () {
    var REGION_LEVEL = 1;
    var DISTRICT_LEVEL = 2;
    var CITY_LEVEL = 3;
    var VILAGE_LEVEL = 4;
    var STREET_LEVEL = 5;
    var HOUSE_LEVEL = 6;
    var CODE_TO_LEVEL = {0: REGION_LEVEL,
                         2: DISTRICT_LEVEL,
                         5: CITY_LEVEL,
                         8: VILAGE_LEVEL,
                         11: STREET_LEVEL,
                         17: HOUSE_LEVEL};

    function show_kladr(h_el) {
        function create_apartment() {
            $('#id_s_7').prev().nextAll().remove();
            var kladr = $('#kladr');
            var apartment = $('<input type="text" id="id_s_7" />').appendTo(kladr);
            $('<input type="button" value="Выбрать" />').appendTo(kladr).click(function () {
                $('#id_s_text').remove();
                var house_id = "#id_s_" + HOUSE_LEVEL;
                var full_text = new Array();
                var house_number = $(house_id).val();
                if (house_number != '-1') {
                    full_text[full_text.length] = house_number;
                }
                kladr.find('select option:selected').each(function() {
                    var el = $(this);
                    if (el.val() != '-1') {
                        full_text[full_text.length] = el.text();
                    }
                });
                var number_apartment = apartment.val()
                if (number_apartment) {
                    full_text[full_text.length] = apartment.val();
                }
                $(h_el).val(full_text.join(', '));
                $('span.b-close').click();
                kladr.html('&nbsp;');
            });
        }

        function create_house(code) {
            $('#id_s_' + HOUSE_LEVEL).prev().nextAll().remove();
            var url = "/kladr.json?level=6&code=" + code;
            $.getJSON(url, function(data) {
                var select = $('<select id="id_s_' + HOUSE_LEVEL + '" name="s_' + HOUSE_LEVEL + '" />');
                for (var val in data) {
                    $("<option />", {value: data[val], text: val}).appendTo(select);
                }
                select.appendTo('#kladr').change(create_apartment).change();
            }); 
        }

        function create_district(code) {
            curr_level = CODE_TO_LEVEL[code.length]
            $('#id_s_' + curr_level).prev().nextAll().remove();
            var url = "/kladr.json?level=" + curr_level;
            url = url + '&code=' + code;
            $.getJSON(url, function(data) {
                var select = $('<select id="id_s_' + curr_level + '" name="s_' + curr_level + '" />');
                select.appendTo('#kladr')
                for (var name_option in data) {
                    var opt_group = $('<optgroup />').attr('label', name_option);
                    opt_group.appendTo(select);
                    for (var val in data[name_option]) {
                        var option_params = {value: data[name_option][val].id,
                                             text: data[name_option][val].value}
                        $("<option />", option_params).appendTo(opt_group);
                    }
                }
                select.change(function(data) {select_callback(this)}).change();
            });
        }

        function select_callback(element) {
            $(element).nextAll().remove();
            curr_level = CODE_TO_LEVEL[element.value.length];
            if (curr_level != HOUSE_LEVEL) {
                return create_district(element.value);
            } else {
                return create_house(element.value);
            }
            
        }

        $('#popup_kladr').bPopup({follow: [false, false],
                                  width: 1024,
                                  position: [0, $(h_el).offset().top + 50],
                                  positionStyle: 'absolute'});
        create_district('', create_district);
    }
    $('#id_registration, #id_residence').click(function() {show_kladr(this)});
});
