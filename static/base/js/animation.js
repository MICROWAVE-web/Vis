let socials = ['Youtube', 'VK', 'Soundcloud', 'Facebook'];

let last_social = 'Youtube'

window.onload = function () {
    animate(last_social);
    $(".soc_item").on("click", function () {
        animate(this.id);
    });

    $('.link_input').bind('keyup', function() {
        let $this = $(this),
            val = $this.val();

        if (val.length > 0) {
            $(this).parent().children('.close_span').css('opacity', '1');
        } else if (val.length === 0) {
           $(this).parent().children('.close_span').css('opacity', '0');
        }
    });

    $('.close_span').on('click', function () {
        this.previousElementSibling.value = ''
        $(this).parent().children('.close_span').css('opacity', '0');
        $('.browse_link').html('<img class="status_gif" src="/static/base/icons/await.gif">')
    })

};

function animate(chosen_social) {
    $('.extra_dots_part').children('#' + socials.indexOf(last_social)).css('color', 'white')
    $('.extra_dots_part').children('#' + socials.indexOf(chosen_social)).css('color', 'black')
    $('.principal_part').children('#' + last_social).removeClass();
    if (socials.indexOf(chosen_social) > socials.indexOf(last_social)) {
        $('.principal_part').children('#' + last_social).addClass("principal_block_up");
    } else if (socials.indexOf(chosen_social) < socials.indexOf(last_social)) {
        $('.principal_part').children('#' + last_social).addClass("principal_block_down");
    }
    $('.principal_part').children('#' + chosen_social).removeClass();
    $('.principal_part').children('#' + chosen_social).addClass("principal_block");
    last_social = chosen_social
}



function getRandomInt() {
  min = Math.ceil(0);
  max = Math.floor(360);
  return Math.floor(Math.random() * (max - min)) + min; //Максимум не включается, минимум включается
}

let i = 0, howManyTimes = 9999999;
function f() {
    i++;
    if( i < howManyTimes ){
        setTimeout( f, 5000 );
    }
}
f();


