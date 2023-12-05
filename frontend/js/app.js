$(document).ready(function () {
    // Show the custom dropdown when "Others" is selected
    $('#leave_type').change(function () {
        if ($(this).val() === 'Others') {
            console.log('yes')
            $('#other_leave_options').show();
        } else {
            $('#other_leave_options').hide();
            console.log('yes')
        }
    });
    
    // Add date restrictions and formal alert messages upon form submission
    $('#leave-form').submit(async function (event) {
        var today = new Date();
        var waitDate = 7; // Adjust this to the employer's wait date in days
        today.setDate(today.getDate() + waitDate); // Add waitDate days to today's date
        var leaveStartDate = new Date($('#leave_start_date').val());
        var leaveEndDate = new Date($('#leave_end_date').val());
        
        if (leaveStartDate >= leaveEndDate) {
            alert('Error: Leave start date should be earlier than the leave end date.');
            $('#leave_start_date').val('');
            $('#leave_end_date').val('');
            event.preventDefault(); // Prevent form submission
            return false; // Cancel the form submission
        } else if (leaveStartDate <= today || leaveEndDate <= today) {
            alert('Error: Leave start and end dates must be at least ' + waitDate + ' days from today.');
            $('#leave_start_date').val('');
            $('#leave_end_date').val('');
            event.preventDefault(); // Prevent form submission
            return false; // Cancel the form submission
        } else {
            // All conditions passed, proceed with the POST request
            const formData = new FormData(this);
            const formDataObject = {};
            formData.forEach((value, key) => {
                formDataObject[key] = value;
            });

            // Send a POST request with the form data
            const response = await fetch("/submit_leave_request", {
                method: "POST",
                body: JSON.stringify(formDataObject), // Convert form data to JSON
                headers: {
                    "Content-Type": "application/json",
                },
            })
            .then(response => response.json())
            .then(data => {
                console.log(data)
                console.log(data.url)
                if (data.url)
                    window.location.replace(data.url); // or, location.replace(data.url);
                else
                    document.getElementById("response").innerHTML = data;
            });
        }
    });
});

