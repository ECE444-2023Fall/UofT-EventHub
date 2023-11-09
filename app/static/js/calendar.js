document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth', 

        views: {
            week: { 
                type: 'dayGridWeek',
                duration: { weeks: 1 },
                buttonText: 'Week'
            },
                list: { 
                type: 'listMonth',
                buttonText: 'List'
            }
        },

        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,dayGridWeek,listDay' 
        },

        events: [
        {
            title: 'Meeting',
            start: '2023-11-15T10:00:00',
            end: '2023-11-15T12:00:00',
            backgroundColor: '#007bff',
            borderColor: '#007bff'
        },
        {
            title: 'Lunch',
            start: '2023-11-16T12:30:00',
            end: '2023-11-16T13:30:00',
            backgroundColor: '#28a745',
            borderColor: '#28a745'
        },
        {
            title: 'Workshop',
            start: '2023-11-17T14:00:00',
            end: '2023-11-17T16:00:00',
            backgroundColor: '#dc3545',
            borderColor: '#dc3545'
        }
         ]
    });

    calendar.render();
});