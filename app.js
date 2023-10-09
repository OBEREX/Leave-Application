 // Show the custom dropdown when "Others" is selected
 $(document).ready(function () {
    $('#leave_type').change(function () {
        if ($(this).val() === 'others') {
            $('#other_leave_options').show();
        } else {
            $('#other_leave_options').hide();
        }
    });
    
    // Add date restrictions and formal alert messages upon form submission
    $('#leave-form').submit(function (event) {
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
        } else if (leaveStartDate <= today || leaveEndDate <= today) {
            alert('Error: Leave start and end dates must be at least ' + waitDate + ' days from today.');
            $('#leave_start_date').val('');
            $('#leave_end_date').val('');
            event.preventDefault(); // Prevent form submission
        }
    });
});