function deleteRecord(id) {
    var amount = $('#amount-take-' + id).val();
    $.ajax({
        url: '/delete/' + id,
        type: 'DELETE',
        data: JSON.stringify({amount: amount}),
        contentType: 'application/json',
        success: function() {
            window.location.reload();
        }
    });
}