$(document).ready(() => {
    const updateTextAreaValue = (e) => {
        const value = e.target.value
        $('#spatial-field-wrapper textarea').val(value)
    }
    $('#spatial-field-wrapper select').on('change', updateTextAreaValue)
})
