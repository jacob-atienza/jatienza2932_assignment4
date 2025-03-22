const postBox = document.getElementById("post-box");
const alertBox = document.getElementById("alert-box");
const backBtn = document.getElementById("back-btn");
const updateBtn = document.getElementById("update-btn");
const deleteBtn = document.getElementById("delete-btn");
const url = window.location.href + "data/";
const updateUrl = window.location.href + "update/";
const deleteUrl = window.location.href + "delete/";

const updateForm = document.getElementById("update-form");
const deleteForm = document.getElementById("delete-form");
const spinnerBox = document.getElementById("spinner-box");

const titleInput = document.getElementById("id_title");
const descriptionInput = document.getElementById("id_description");
const csrf = document.getElementsByName("csrfmiddlewaretoken");
//backBtn.addEventListener("click", () => {
//  history.back();
//});

$.ajax({
  type: "GET",
  url: url,
  success: (response) => {
    console.log(response);
    const data = response.data;

    if (data.logged_in !== data.author) {
      console.log("different");
    } else {
      console.log("same");
      updateBtn.classList.remove("not-visible");
      deleteBtn.classList.remove("not-visible");
    }

    const titleEl = document.createElement("h3");
    titleEl.setAttribute("class", "mt-3");
    titleEl.setAttribute("id", "title");

    const descriptionEl = document.createElement("p");
    descriptionEl.setAttribute("class", "mt-1");
    descriptionEl.setAttribute("id", "description");

    titleEl.textContent = data.title;
    descriptionEl.textContent = data.description;
    console.log(postBox);

    postBox.appendChild(titleEl);
    postBox.appendChild(descriptionEl);

    titleInput.value = data.title;
    descriptionInput.value = data.description;

    spinnerBox.classList.add("not-visible");
  },
  error: (error) => {
    console.log(error);
  },
});

updateForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const title = document.getElementById("title");
  const description = document.getElementById("description");

  $.ajax({
    type: "POST",
    url: updateUrl,
    data: {
      csrfmiddlewaretoken: csrf[0].value,
      title: titleInput.value,
      description: descriptionInput.value,
    },
    success: (response) => {
      $("#updateModal").modal("hide");
      console.log(response);
      handleAlerts("success", "Post has been updated");
      title.textContent = response.title;
      description.textContent = response.description;
    },
    error: (error) => {
      console.log(error);
    },
  });
});

deleteForm.addEventListener("submit", (e) => {
  e.preventDefault();

  $.ajax({
    type: "POST",
    url: deleteUrl,
    data: {
      csrfmiddlewaretoken: csrf[0].value,
    },
    success: (response) => {
      window.location.href = window.location.origin;
      localStorage.setItem("title", titleInput.value);
      console.log(response);
    },
    error: (error) => {
      console.log(error);
    },
  });
});
