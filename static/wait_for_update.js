async function waitForUpdate() {
    setTimeout(function () {
        data = new Object();
        fetch("wait-field-update", {
            method: 'POST',
            headers: new Headers({
                'Content-Type': 'application/json'
            }),
            body: JSON.stringify(data) 
        })
            .then((response) => response.text())
            .then((responseText) => {
                if (responseText.length == 0 || responseText.startsWith("RELOAD")) {
                    location.reload();
                } else if (responseText.startsWith("UPDATE:")) {
                    location.reload();
                } else if (responseText == "WAIT") {
                    waitForUpdate();
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
    }, 300)
}

waitForUpdate();
