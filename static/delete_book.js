// Find delete buttons, add click listeners.

buttons = document.getElementsByClassName('delete_book');

for ( b = 0 ; b < buttons.length ; b++) {
  buttons[b].addEventListener('click', deleteBook);
}


function deleteBook() {

  if (confirm('Delete book: are you sure?')) {

    var book_id = this.value

    //AJAX request. Async request, once response received from server, can update page.
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
      //If AJAX call has returned, and the response code is success,
      if (this.readyState == 4 && this.status == 200) {
        // remove div with book in
        delete_div = document.getElementById("book_" + book_id);
        console.log(book_id)
        console.log(delete_div)

        //deleting is weird - find the element's parent, and ask it
        //to delete the child. Can't ask an element to delete itself.
        delete_div.parentNode.removeChild(delete_div);

        // If the server says deleted (vs the element request to be deleted not found) then
        // reduce the count by 1. Another approach would be to not use AJAX and just refresh the
        // page after delete. AJAX is more responsive and saves a database query. (delete vs. delete + query)
        if (this.response == 'deleted') {
          try {
            book_count = document.getElementById('book_count');
            current_count = parseInt(book_count.innerText) - 1 ;
            book_count.innerText = current_count;
          } catch(err) {
            //leave element as is.
          }
        }

      }
    }

    xhttp.open('DELETE', '/book/' + book_id, true);
    xhttp.send();

  }

}
