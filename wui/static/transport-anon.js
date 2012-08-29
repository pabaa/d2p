$(function() {

$('#anon_bootstrap_addform').submit(function() {
    var bsType = $('#anon_bootstrap_type').val();
    var q = {'bsType': bsType};
    var url = '/_transports/p2p/bootstrap/';
    d2p.sendQuery(url, q, function() {
        d2p.content_goto('/_transports/p2p/');
    });
});

$('.anon_bootstrap[data-bootstrap-type="manual"]').each(function(i, el) {
    var bsEl = $(el);

    var entryTable = bsEl.find('.anon_bootstrap_entries');
    var newRow = $('<tr class="anon_bootstrap_newRow">');

    var transportIds = ['anon-tor/i2p'];
    var inputTransportIds = $('<select>');
    _.each(transportIds, function(ti) {
        var opt = $('<option>');
        opt.attr({'value': ti});
        opt.text(ti);
        inputTransportIds.append(opt);
    });
    var td = $('<td>');
    inputTransportIds.appendTo(td);
    td.appendTo(newRow);

    var inputAddr = $('<input type="text" required="required">');
    inputAddr.attr({'placeholder': d2p.i18n('remote Destination string')});
    var td = $('<td>');
    inputAddr.appendTo(td);
    td.appendTo(newRow);

    var submit = $('<input type="button">');
    submit.attr({value: d2p.i18n('Add entry')});
    submit.appendTo(td);
    td.appendTo(newRow);

    submit.click(function() {
        var entry = {
            'transportId': inputTransportIds.val(),
            'addr': inputAddr.val(),
        };

        var url = '/_transports/p2p/bootstrap/' + bsEl.attr('data-bootstrap-id') + '/manual/entries/';
        d2p.sendQuery(url, entry, function() {
            d2p.content_goto('/_transports/p2p/');
        });
    });
    
    entryTable.find('tbody').append(newRow);
});

});
