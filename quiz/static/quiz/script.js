const collection = document.getElementById("wrapper").children;


function makeRequired1(x) {
    let control = collection[x].getElementsByClassName("form-control");
    for (let j = 0; j < 6; j++) {
        control[j].required = true
  }
}


function makeRequired(x) {
    let control = collection[x].getElementsByClassName("form-control");
    for (let j = 0; j < 6; j++) {
        if([0,1,2,5].includes(j)) {
            console.log(j)
            control[j].required = true
        }
  }
}

//Makes all fields in the first 5 forms required
for (let i = 0; i < 5; i++) {
      makeRequired(i)
  }


let counter=5

function showExtra() {
    collection[counter].style.display = "block"
    if (counter>19){
        document.getElementById("addQuestion").disabled = true;
    }
    makeRequired(counter)
    counter+=1
}



//AJAX
function getData(url, id) {
    fetch(url, {
        method: "GET",
        headers: {
            "X-Requested-With": "XMLHttpRequest",
        }
        })
    .then(response => response.json())
    .then(data => {
    


    if (data.comments.find(comment => comment.id == id)){
        let commentrating = data.comments.find(comment => comment.id == id)['rating']
        document.getElementById('comment-'+ id).innerHTML = commentrating
    }

    let quizrating = data.quiz['rating']
    document.getElementById('quizrating').innerHTML = quizrating
    
});
}


//Django provided function to get the csrf cookie needed to post data https://docs.djangoproject.com/en/3.0/ref/csrf/#ajax
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + "=")) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}


function updateData(url, payload) {
    fetch(url, {
        method: "PUT",
        credentials: "same-origin",
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken"),  // don't forget to include the 'getCookie' function
        },
        body: JSON.stringify({payload: payload})
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        });
}

// Not in use
function updateQuizData(url, payload) {
    fetch(url, {
        method: "PUT",
        credentials: "same-origin",
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken"),  // don't forget to include the 'getCookie' function
        },
        body: JSON.stringify({payload: payload})
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        });
}


function report(url, payload){
fetch(url, {
  method: "POST",
  credentials: "same-origin",
  headers: {
    "X-Requested-With": "XMLHttpRequest",
    "X-CSRFToken": getCookie("csrftoken"),
  },
  body: JSON.stringify({payload: payload})
})
.then(response => response.json())
.then(data => {
  console.log(data);
});
}

