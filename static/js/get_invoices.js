$(document).ready(function() {
    $('form').on('submit', function(event) {
        event.preventDefault();
        $.ajax({
            url: '/receipt',
            type: 'POST',
            data: $('form').serialize(),
            success: function(data) {
                var table = '<table><thead><tr><th>№</th><th>Название материала</th><th>Количество</th><th>Дата получения</th></tr></thead><tbody>';
                for (var i = 0; i < data.length; i++) {
                    table += '<tr><td>' + (i+1) + '</td><td>' + data[i].material_name + '</td><td>' + data[i].quantity + '</td><td>' + data[i].receipt_date + '</td></tr>';
                }
                table += '</tbody></table>';
                $('#results').html(table);
            }
        });
    });
});