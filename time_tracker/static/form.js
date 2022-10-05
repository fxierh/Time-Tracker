/**
 * Enable submit button if form is changed, disable submit button otherwise.
 */
function update_submit_button_state (){
    if (form.serialize() !== form.data('serialize')) {
        submit_button.removeClass('disabled');
    }
    else {
        submit_button.addClass('disabled');
    }
    return true
}

/**
 * Disable form submit on Enter
 * @param evt
 * @returns {boolean}
 */
function disable_enter_submit (evt) {
    if (evt.key === 'Enter') {
        evt.preventDefault();
        return false;
    }
}

