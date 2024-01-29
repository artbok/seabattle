var cd = 0;
async function fire(x, y) {
    data = new Object();
    data.x = x;
    data.y = y;
    cd += 2
    fetch("fire", {
        method: 'POST',
        headers: new Headers({
            'Content-Type': 'application/json',
        }),
        body: JSON.stringify(data)  
    })
        .then((response) => response.text())
        .then((responseText) => {
            if (responseText.startsWith("Error"))
                alert("В эту клетку уже стреляли!");
            else if (responseText.startsWith("notYourMove"))
                alert("Сейчас не твой ход!");
            else if (responseText.startsWith("NOAMMO"))
                alert("У вас кончились выстрелы!");   
            else if (responseText.startsWith("HIT") || (responseText.startsWith("MISS")))
                location.reload();
        })
        .catch((error) => {
            console.error(error);
            alert("FIRE server error: " + error);
        });
}

async function waitForUpdate() {
    setTimeout(function () {
        data = new Object();
        if (cd == 0) {
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
        } else {
            cd -= 1
            waitForUpdate()
        }
    }, 250)
}
waitForUpdate();
