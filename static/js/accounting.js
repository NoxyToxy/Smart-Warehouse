$(document).ready(function() {
    $('form').on('submit', function(event) {
        event.preventDefault();
        $.ajax({
            url: '/accounting',
            type: 'POST',
            data: $('form').serialize(),
            success: function(data) {
                var table = '<table><thead><tr><th>Получение</th><th>Выдача</th></tr></thead><tbody>';
                var receipt = data[0].receipt;
                var issuance = data[0].issuance;
                var receiptLength = receipt.length;
                var issuanceLength = issuance.length;
                var maxLength = Math.max(receiptLength, issuanceLength);
                for (var i = 0; i < maxLength; i++) {
                    var receiptRow = '';
                    var issuanceRow = '';
                    if (i < receiptLength) {
                        receiptRow = '<td>' + receipt[i].name + ' || ' + receipt[i].amount + ' pcs</td>';
                    } else {
                        receiptRow = '<td></td>';
                    }
                    if (i < issuanceLength) {
                        issuanceRow = '<td>' + issuance[i].name + ' || ' + issuance[i].amount + ' pcs || ' + issuance[i].fullname + '</td>';
                    } else {
                        issuanceRow = '<td></td>';
                    }
                    table += '<tr>' + receiptRow + issuanceRow + '</tr>';
                }
                table += '</tbody></table>';
                $('#results').html(table);
            }
        });
    });
});