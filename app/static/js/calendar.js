document.addEventListener('DOMContentLoaded', function() {
    var eventData = JSON.parse(event_data_json.innerText);
        console.log(eventData);
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',  // Default view is set to list

        views: {
            dayGridMonth: {
                buttonText: 'Month'
            },
            dayGridWeek: { 
                type: 'dayGridWeek',
                duration: { weeks: 1 },
                buttonText: 'Week'
            },
            list: { 
                type: 'listMonth', // This will give you a list view with a monthly format
                buttonText: 'Day'
            }
        },

        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,dayGridWeek,listMonth'
        },

        eventClick: function(info) {
                eventKey = info.event.extendedProps.key;
                window.location.href = `/events/${eventKey}` ;
            },

        events: eventData,
        
    });

    calendar.render();
});