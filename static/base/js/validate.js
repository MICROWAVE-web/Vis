$(document).ready(function () {
    // catch the form's submit event
      $('.link_input').bind('keyup', function() {
        $('.browse_link').html('<img class="status_gif" src="https://c.tenor.com/I6kN-6X7nhAAAAAi/loading-buffering.gif">')
        let $this = $(this),
            val = $this.val();
        if (val.length === 0) {
            $('.browse_link').html('<img class="status_gif" src="/static/base/icons/await.gif">')
            return false
        };
        // create an AJAX call
        $.ajax({
            dataType: 'json',
            data: {'url': val}, // get the form data
            url: '../' + "ajax_validate_url/",
            // on success
            success: function (response) {
                if (response.is_actual[0] === true) {
                    $('.browse_link').html('<img class="big_status_gif" src="/static/base/icons/ok.gif">')
                    console.log(response.streams)
                    $('.info_link').text(response.streams[0]['url'])
                } else {
                    $('.browse_link').html('<img class="big_status_gif" src="/static/base/icons/cross.gif">')
                    $('.info_link').text(response.streams)
                }

            },
            error: function (response) {
                $('.browse_link').html('<img class="big_status_gif" src="/static/base/icons/cross.gif">')
            }
        });

        return false;
    });
})