async function cellUpdate(x, y) {
    data = new Object();
    data.x = x;
    data.y = y;

    fetch("field-cell-update", {
        method: 'POST',
        headers: new Headers({
            'Content-Type': 'application/json', // <-- Specifying the Content-Type
        }),
        body: JSON.stringify(data)  // + "&val=" + val // <-- Post parameters
    })
        .then((response) => response.text())
        .then((responseText) => {
            if (responseText.length == 0)
                location.reload();
            else
                alert("Вы не можете поставить сюда корабль!");
        })
        .catch((error) => {
            console.error(error);
            alert("server error: " + error);
        });


    // alert("click x:" + x + ", y:" + y + ", v:" + val)
}