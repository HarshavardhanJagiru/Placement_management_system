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

    // Real-time job filtering on student dashboard
    $('#jobSearch').on('keyup', function() {
        const query = $(this).val().toLowerCase();
        $('.job-card').each(function() {
            const position = $(this).find('.card-title').text().toLowerCase();
            const company = $(this).find('.card-company').text().toLowerCase();
            
            if (position.includes(query) || company.includes(query)) {
                $(this).fadeIn();
            } else {
                $(this).fadeOut();
            }
        });
    });

    // Custom Toast Notification simulation using Alerts
    if ($('.alert').length) {
        $('.alert').addClass('shadow-lg animate__animated animate__fadeInRight');
    }
});
