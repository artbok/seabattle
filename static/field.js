async function cellUpdate(x, y, val) {
    data = new Object();
    data.x = x;
    data.y = y;
    data.val = val;

    fetch("field-cell-update", {
        method: 'POST',
        headers: new Headers({
            'Content-Type': 'application/json', // <-- Specifying the Content-Type
        }),
        body: JSON.stringify(data)  // + "&val=" + val // <-- Post parameters
    })
        .then((response) => response.text())
        .then((responseText) => {
            location.reload()
        })
        .catch((error) => {
            console.error(error);
        });


    // alert("click x:" + x + ", y:" + y + ", v:" + val)
}