// Placement Management System - jQuery behavior
$(document).ready(function() {
    console.log('Placement Management System Initialized with jQuery');

    // Form validation for Login & Register
    $('form').on('submit', function(e) {
        let isValid = true;
        let errorMessage = "";

        $(this).find('input[required]').each(function() {
            if ($(this).val().trim() === "") {
                isValid = false;
                $(this).addClass('is-invalid');
                errorMessage = "Please fill in all required fields.";
            } else {
                $(this).removeClass('is-invalid');
            }
        });

        // Email validation if email field exists
        const emailField = $(this).find('input[type="email"]');
        if (emailField.length && emailField.val()) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(emailField.val())) {
                isValid = false;
                emailField.addClass('is-invalid');
                errorMessage = "Please enter a valid email address.";
            }
        }

        if (!isValid) {
            e.preventDefault();
            alert(errorMessage);
        }
    });

    // Fade out alerts after 3 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 3000);

    // Simple UI effect: Highlight table rows on hover
    $('tbody tr').hover(
        function() { $(this).addClass('bg-light'); },
        function() { $(this).removeClass('bg-light'); }
    );
});
