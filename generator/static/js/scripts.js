
var t = [{'a':1, 'b':2}, {'a':2, 'b':3}];
var newData = [];

function check(){
    var tok = document.getElementsByName('csrfmiddlewaretoken')[0];

    var re = /&#x27;/gi;
    var b = a.replace(re, '"');

    var data = {
        'csrfmiddlewaretoken' : ''+tok.attributes['value']['value'],
        content : b,
        newContent: JSON.stringify(newData)
    };

    $.ajax({
    data: data,
    method: 'POST',
    url: uri,
    success: function (response) {
        if (response.is_taken == true){
            newData = newData.concat(response.data);
            response.data.forEach(function(item, i, arr){
                $('#r'+item.aNum+''+item.interval).append(item.room)
                $('#s'+item.aNum+''+item.interval).append(item.secName)
            })
        }
    }
    });
    return false;
}

function onBtn(){
    var nowTime = new Date();
    var cmpTime = new Date();
    cmpTime.setHours(7, 30);
    if (nowTime >= cmpTime){
        $('#sBtn').prop('disabled', false);
    } else {
        $('#sBtn').prop('disabled', true);
    }
}

$(document).ready(function(){
    check();
    setInterval('check()', 1000);
    setInterval('onBtn()', 1000);

});