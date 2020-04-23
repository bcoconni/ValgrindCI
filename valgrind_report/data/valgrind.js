$(document).ready(
    function () {
        $(".visibility_call_stack").button();
        $(".visibility_call_stack").click(function () {
            $(this).parents("table").find("tr.stack_frame").toggle();
        });
        $("table.call_stack tr.stack_frame").hide();
        $("button.next_error").button();
        $("button.next_error").click(function () {
            var index = $(this).parents("table").index("table.call_stack");
            $([document.documentElement, document.body]).animate({
                scrollTop: $("table.call_stack").eq(index + 1).offset().top
            }, 500);
        });
        $("button.next_error:last").hide();
        $("button.prev_error").button();
        $("button.prev_error").click(function () {
            var index = $(this).parents("table").index("table.call_stack");
            $([document.documentElement, document.body]).animate({
                scrollTop: $("table.call_stack").eq(index - 1).offset().top
            }, 500);
        });
        $("button.prev_error:first").hide();
    });
