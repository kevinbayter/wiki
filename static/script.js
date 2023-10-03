function addComment(parentCommentId = null) {
    const commentInput = parentCommentId ? document.getElementById(`reply-input-${parentCommentId}`) : document.getElementById('comment-input');
    const comment = commentInput.value.trim();

    if (comment) {
        fetch('/add-comment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ comment: comment, parent_comment_id: parentCommentId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const commentHtml = `
                    <div class="comment-item" data-comment-id="${data.comment_id}">
                        <img src="/static/uploads/${data.profile_picture}" alt="${data.username}" width="40" height="40">
                        <div class="comment-content">
                            <div class="comment-author">${data.username}</div>
                            ${comment}
                            <button onclick="showReplyBox(${data.comment_id})">Responder</button>
                            <div class="comment-reply"></div>
                        </div>
                    </div>
                `;

                if (parentCommentId) {
                    const parentCommentReplyContainer = document.querySelector(`.comment-item[data-comment-id="${parentCommentId}"] .comment-reply`);
                    parentCommentReplyContainer.innerHTML += commentHtml;
                } else {
                    const commentsList = document.querySelector('.comments-container');
                    commentsList.innerHTML += commentHtml;
                }

                commentInput.value = '';
            }
        });
    }
}

function submitReply(buttonElement, parentCommentId) {
    const textarea = buttonElement.previousElementSibling;
    const reply = textarea.value;
    if(reply.trim() === '') {
        alert('Por favor, escribe una respuesta.');
        return;
    }

    // Enviar la respuesta al servidor
    fetch('/add-comment', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            comment: reply,
            parent_comment_id: parentCommentId
        })
    })
    .then(response => response.json())
    .then(data => {
        if(data.success) {
            // Actualizar la UI o recargar la página para ver la respuesta
            location.reload();
        } else {
            alert('Hubo un error al enviar la respuesta.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Hubo un error al enviar la respuesta.');
    });
}

function replyComment(buttonElement) {
    // Oculta todos los formularios de respuesta abiertos previamente
    const allReplyForms = document.querySelectorAll('.reply-form');
    allReplyForms.forEach(form => form.style.display = 'none');

    // Muestra el formulario de respuesta para el comentario actual
    const currentReplyForm = buttonElement.nextElementSibling;
    currentReplyForm.style.display = 'block';
}

function showReplyBox(commentId) {
    const replyBox = document.getElementById(`reply-box-${commentId}`);
    if (replyBox) {
        replyBox.style.display = 'block';
    } else {
        const commentItem = document.querySelector(`.comment-item[data-comment-id="${commentId}"]`);
        const replyContainer = commentItem.querySelector('.comment-reply');

        const replyBox = document.createElement('textarea');
        replyBox.id = `reply-input-${commentId}`;
        replyBox.placeholder = "Escribe tu respuesta...";

        const replyButton = document.createElement('button');
        replyButton.textContent = "Responder";
        replyButton.onclick = function() {
            addComment(commentId);
            replyBox.remove();
            replyButton.remove();
            cancelButton.remove();
        };

        const cancelButton = document.createElement('button');
        cancelButton.textContent = "Cancelar";
        cancelButton.onclick = function() {
            replyBox.remove();
            replyButton.remove();
            cancelButton.remove();
        };

        replyContainer.appendChild(replyBox);
        replyContainer.appendChild(replyButton);
        replyContainer.appendChild(cancelButton);
    }
}

function deleteComment(commentId) {
    // Llama al endpoint para eliminar el comentario
    fetch(`/delete-comment/${commentId}`, {
        method: 'DELETE'
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              const commentItem = document.querySelector(`.comment-item[data-comment-id="${commentId}"]`);
              commentItem.remove();
          } else {
              alert(data.message);
          }
      });
}

function showReplyBox(commentId) {
    const replyBox = document.getElementById(`reply-box-${commentId}`);
    replyBox.style.display = 'block';
}

function hideReplyBox(commentId) {
    const replyBox = document.getElementById(`reply-box-${commentId}`);
    replyBox.style.display = 'none';
}
