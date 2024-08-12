$(document).ready(() => {
    const updateTextAreaValue = (e) => {
        const value = e.added.id
        $('#spatial-field-wrapper textarea').val(value)
    }
    $('#spatial-field-wrapper input[type="text"]').on('change', updateTextAreaValue)
})
