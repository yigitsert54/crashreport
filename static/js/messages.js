// close message event
$("div.messageBox button.btn-close").on("click", function () {
    // Extract all message boxes
    var allMessageBoxes = document.querySelectorAll("div.messageBox");

    // Loop through each message box
    allMessageBoxes.forEach(messageBox => {

        // Add close class
        messageBox.classList.add("close");
    });
});
