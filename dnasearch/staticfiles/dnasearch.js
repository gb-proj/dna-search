

const csrftoken = getCookie('csrftoken');

// load user searches on page load
fetch("/user-searches/")
.then(function (response) {
    response.json().then(function(json) {
        let table = document.getElementById("dna_search_results");
        table.innerHTML = JSON.stringify(json);
    });
});

// autorefresh

// add form event listener to submit a new search
document.addEventListener('submit', function (event) {

	event.preventDefault();

	let json_body = JSON.stringify(Object.fromEntries(new FormData(event.target)));

    fetch('/start-search/', {
		method: 'POST',
        body: json_body,
		headers: {
            'X-CSRFToken': csrftoken,
			'Content-type': 'application/json; charset=UTF-8'
		}
	}).then(function (response) {
		if (response.ok) {
			return response.json();
		}
		return Promise.reject(response);
	}).then(function (data) {
		console.log(data);
	}).catch(function (error) {
		console.warn(error);
	});
});


// Django-provided method to resolve csrf cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}