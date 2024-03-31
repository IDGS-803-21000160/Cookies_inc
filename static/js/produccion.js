
function solicitarProduccion(idButton, idProducto) {
    //Desactivar el boton
    document.getElementById(idButton).disabled = true

    const url = `/agregarProduccion?idProducto=${idProducto}`;

    // Make AJAX request to get ventas data for the selected week
    fetch(url)
        .then(response => response.json())
        .then(data => {
            console.log(data);
            if (data.response == 'success'){
                console.log('success')
                
            }
            
        })
        .catch(error => console.error('Error:', error));
}


function producir(idButton, id, inputCantidad,idProduccionitem){

    //Desactivar el boton
    document.getElementById(idButton).disabled = true;
    cantidad = document.getElementById('cuantas_'+inputCantidad).value;
    console.log(cantidad);
    var url = '/descontarProduccion?idProducto=' + encodeURIComponent(id) + '&cantidad=' + encodeURIComponent(cantidad)+ '&idProduccionitem=' + encodeURIComponent(idProduccionitem);

    // Make AJAX request to get ventas data for the selected week
    fetch(url)
        .then(response => response.json())
        .then(data => {
            console.log(data);
            if (data.response == 'success'){   
                location.reload();
            }
        })
        .catch(error => console.error('Error:', error));
}