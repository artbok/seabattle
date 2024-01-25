async function waitForUpdate() {
    setTimeout(function () {
        data = new Object();
        fetch("wait-field-update", {
            method: 'POST',
            headers: new Headers({
                'Content-Type': 'application/json', // <-- Specifying the Content-Type
            }),
            body: JSON.stringify(data)  // + "&val=" + val // <-- Post parameters
        })
            .then((response) => response.text())
            .then((responseText) => {
                if (responseText.length == 0 || responseText.startsWith("RELOAD")) {
                    location.reload();
                } else if (responseText.startsWith("UPDATE:")) {
                    location.reload();
                } else if (responseText == "WAIT") {
                    waitForUpdate();
                    ; //console.log("wait");
                } else {
                    alert("получена команда:" + responseText);
                    waitForUpdate();
                }
            })
            .catch((error) => {
                waitForUpdate();
                console.error(error);
                alert("waitForUpdate: server error: " + error);
            });
        // waitForUpdate();
    }, 250)
}

waitForUpdate();
