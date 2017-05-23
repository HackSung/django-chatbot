$(function() {
    // When we're using HTTPS, use WSS too.
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var chatsock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/chat" + window.location.pathname);
    
    chatsock.onmessage = function(message) {
        var data = JSON.parse(message.data);
        var chat_div = "";

        if (data.handle == "Watson") {
            chat_div = '<div class="row msg_container base_receive"> \
                            <div class="col-md-2 col-xs-2 avatar"> \
                                <img src="https://avatars.slack-edge.com/2017-04-28/175249502928_e953aa49341fe733642b_72.png" class=" img-responsive "> \
                            </div> \
                            <div class="col-md-10 col-xs-10"> \
                                <div class="messages msg_receive"> \
                                    <p>' + data.message + '</p> \
                                    <time datetime="2009-11-13T20:00">' + data.handle + '•' + data.timestamp + '</time> \
                                </div> \
                            </div> \
                        </div>'
        } else {
            chat_div = '<div class="row msg_container base_sent"> \
                            <div class="col-md-10 col-xs-10"> \
                                <div class="messages msg_sent"> \
                                    <p>' + data.message + '</p> \
                                    <time datetime="2009-11-13T20:00">' + data.handle + '•' + data.timestamp + '</time> \
                                </div> \
                            </div> \
                            <div class="col-md-2 col-xs-2 avatar"> \
                                <img src="http://www.bitrebels.com/wp-content/uploads/2011/02/Original-Facebook-Geek-Profile-Avatar-1.jpg" class=" img-responsive "> \
                            </div> \
                        </div>';
        }

        var chat = $("#chat")
        chat.append(chat_div)
        var d = $('.msg_container_base');
        d.scrollTop(d.prop("scrollHeight"));
    };

    $("#btn-chat").on("click", function(event) {
        var message = {
            handle: $('#handle').val(),
            message: $('#btn-input').val(),
        }
        chatsock.send(JSON.stringify(message));
        $("#btn-input").val('').focus();
        return false;
    });

    $("#btn-input").keypress(function(event) {
        if (event.which == 13) {
            event.preventDefault();
            $("#btn-chat").click();
        }
    });
});

$(document).on('click', '.panel-heading span.icon_minim', function (e) {
    var $this = $(this);
    if (!$this.hasClass('panel-collapsed')) {
        $this.parents('.panel').find('.panel-body').slideUp();
        $this.addClass('panel-collapsed');
        $this.removeClass('glyphicon-minus').addClass('glyphicon-plus');
    } else {
        $this.parents('.panel').find('.panel-body').slideDown();
        $this.removeClass('panel-collapsed');
        $this.removeClass('glyphicon-plus').addClass('glyphicon-minus');
    }
});

$(document).on('focus', '.panel-footer input.chat_input', function (e) {
    var $this = $(this);
    if ($('#minim_chat_window').hasClass('panel-collapsed')) {
        $this.parents('.panel').find('.panel-body').slideDown();
        $('#minim_chat_window').removeClass('panel-collapsed');
        $('#minim_chat_window').removeClass('glyphicon-plus').addClass('glyphicon-minus');
    }
});

$(document).on('click', '.icon_close', function (e) {
    $( "#chat_window_1" ).remove();
});