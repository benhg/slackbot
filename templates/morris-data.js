$.getJSON(
    '/_ajax_tree_data', {},
    function(data) {
        Morris.Area({
            element: 'morris-area-chart',
            data: data,
            xkey: 'time',
            labels: ['Eamon', 'Kyle', 'Tyler', 'Ben', 'Theodore', 'Alex', 'Samarth'],
            ykeys: ['Eamon', 'Kyle', 'Tyler', 'Ben', 'Theodore', 'Alex', 'Samarth'],
            pointSize: 2,
            hideHover: 'auto',
            resize: true
        });
    }
);
