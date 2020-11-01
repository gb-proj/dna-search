

const csrftoken = getCookie('csrftoken');

// load user searches on page load
loadUserSearches()

// autorefresh every 5s
window.onload = startInterval;
function startInterval() {
    setInterval("loadUserSearches();", 5000);
}

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

	loadUserSearches();
});

// function to fetch searches for the current user
function loadUserSearches() {
    fetch("/user-searches/")
    .then(function (response) {
        response.json().then(function(json) {
            let table = document.getElementById("dna_search_results");
            table.innerHTML = buildTableRows(json);
        });
    });
}

let TABLE_HEADER = `
<tr>
  <th>Search State</th>
  <th>Search String</th>
  <th>Stared At</th>
  <th>Completed At</th>
  <th>Protein</th>
  <th>Start Location</th>
  <th>End Location</th>
</tr>
`

function buildTableRows(records) {
    // search_state, started_at, completed_at, result_protein, result_start_location, result_end_location
    return TABLE_HEADER + records.map(r => buildTableRow(r)).join('\n');
}

function buildTableRow(record) {
    let searchState = record['search_state'];
    let searchString = record['search_string'];
    let startedAt = record['started_at'];
    let completedAt = record['completed_at'] || '';
    let resultProtein = record['result_protein'] || '';
    let startLocation = record['result_start_location'] || '';
    let endLocation = record['result_end_location'] || '';

    return `
<tr>
  <td>${searchState}</td>
  <td>${searchString}</td>
  <td>${startedAt}</td>
  <td>${completedAt}</td>
  <td>${resultProtein}</td>
  <td>${startLocation}</td>
  <td>${endLocation}</td>
</tr>
`;
}

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