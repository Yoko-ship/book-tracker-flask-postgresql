const main_btn = document.querySelector(".main-btn");
const add_books = document.querySelector(".add-btn");
const show_books = document.querySelector(".books-btn")
const name_input = document.querySelector(".name-input");
const author_input = document.querySelector(".author-input");
const genre = document.querySelector(".genre-input");
const status_input = document.querySelector(".select");
const mark_input = document.querySelector(".mark-input");
const submit_btn = document.querySelector(".submit-btn")
const delete_btn = document.querySelectorAll(".delete-btn")
var edit_btn = document.querySelectorAll(".edit")
var grids = document.querySelectorAll(".grid")





main_btn.addEventListener("click",(event)=>{
    event.preventDefault()
    window.location.href = "/"
})

add_books.addEventListener("click",(event)=>{
    event.preventDefault()
    window.location.href = "/add-books"
})

show_books.addEventListener("click",(event)=>{
    event.preventDefault()
    window.location.href = "/books"
})


// Удаляем элемент
delete_btn.forEach(deleting =>{
    deleting.addEventListener("click",(event)=>{
        const deleted_elements = event.target.parentElement

        //* Получаем id элемента в виде текста
        const text_div = deleted_elements.id
        const replaced_element = text_div.replace("div-","")
        // *  Оправляем перенную в сервер(flask)
        fetch(`/books?id=${replaced_element}`,{
            method:"GET",
        })
        .then((response => response.json()))
        .then(data =>{
            console.log("Ответ от сервера",data)
        })
        .catch((error ) => {
            console.log(error)
        })
        
        deleted_elements.remove()
    })
})

// Добавляем input'ы в div

edit_btn.forEach(edit =>{
        edit.addEventListener("click",(event)=>{
            var parentElem = event.target.parentElement
            var current_id = parentElem.id
            var replaced_id = current_id.replace("div-","")

            var current_button = event.target
            var current_Div = current_button.closest("div")
            var selectElement = document.createElement("select")
            selectElement.classList = "select-button"
            var texts = ["Прочитал","Читаю","Планирую прочесть"]
            for (var text in texts){
                var option = document.createElement("option")
                option.value = texts[text]
                option.innerHTML = texts[text]
                selectElement.appendChild(option)
            }
            var save_button = document.createElement("button")
            save_button.classList = "save-button"
            save_button.innerHTML = "SaveButton"
            current_Div.appendChild(selectElement)
            current_Div.appendChild(save_button)
            save_button.addEventListener("click",()=>{
                const selectValue = selectElement.value
                fetch(`/books?value=${selectValue}&div-id=${replaced_id}`,{
                    method:"GET",
                })
                .then((response => response.json()))
                .then(data =>{
                    console.log(data)
                })
                .catch((error => console.log(error)))
                selectElement.style.display = "none"
                save_button.style.display = "none"
                window.location.reload()
            })
        })
    })


