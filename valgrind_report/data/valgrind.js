$(document).ready(
    function () {
        $("div.issue").accordion({ collapsible: true, active: false });
        $("button.next_error").button();
        $("button.next_error").click(function () {
            var index = $(this).parents("div.issue").index("div.issue");
            $([document.documentElement, document.body]).animate({
                scrollTop: $("div.issue").eq(index + 1).offset().top
            }, 500);
        });
        $("button.next_error:last").hide();
        $("button.prev_error").button();
        $("button.prev_error").click(function () {
            var index = $(this).parents("div.issue").index("div.issue");
            $([document.documentElement, document.body]).animate({
                scrollTop: $("div.issue").eq(index - 1).offset().top
            }, 500);
        });
        $("button.prev_error:first").hide();
    });
