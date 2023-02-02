document.addEventListener('DOMContentLoaded', e => {
    let location = window.location.href;
    document.querySelectorAll('a.nav-link').forEach(element => {
        element.classList.remove('active');
        if (element.href == location) {
            element.classList.add('active');
        }
    });
});

let row;
function saveRow(event) {
    row = event.target.closest('tr').id;
    console.log(row)
    document.querySelector('select#leadRdvCreate').value = row.split('-')[1];
}

function handleReject() {
    axios.post(`/reject/${row.split('-')[1]}`).then(res => {
        console.log(res.data)
        if (res.data.success) {
            document.querySelector(`tr#${row}`).remove();
        }
    })
}

function addReminder(event) {
    event.preventDefault()
    let data = new FormData(event.target)
    axios.post('/reminders', data).then(res => {
        if (res.data.success) {
            window.alert("Rappel enrégistré")
            document.querySelector(`tr#${row}`).remove();
        }
    })
}

function callIn2Week() {
    axios.post(`/callin2week/${row.split('-')[1]}`).then(res => {
        if (res.data.success) {
            window.alert("Rappel enrégistré")
            document.querySelector(`tr#${row}`).remove();
        }
    })
}