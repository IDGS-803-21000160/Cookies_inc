// Función para limpiar los campos de inyecciones SQL
function limpiarCampos(input) {
    // Expresión regular para buscar caracteres que puedan ser utilizados en inyecciones SQL
    var regex = /#[;'"\/\\]/g;
    // Reemplazar caracteres coincidentes con la expresión regular con una cadena vacía
    return input.replace(regex, '');
}

//PRUEBA MIA LOGIN PETICION
$(document).ready(function(){
    $('#login_button').click(function(){
        var username = limpiarCampos($('#username').val());
        var password = limpiarCampos($('#password').val());
        if(username != '' && password != '')
        {
            var dataToSend = JSON.stringify({ username: username, password: password, log: 'valor_del_log' });
            $.ajax({
                url: "http://127.0.0.1:5000/acceso2",
                method: "POST",
                contentType: 'application/json',
                data: dataToSend,
                success: function(data){
                    //console.log(data)
                    if(data.msg)
                    {
                        Swal.fire({
                            icon: "error",
                            title: "Oops...",
                            text: data.msg,
                          });
                        //console.log(data)
                        window.location.href = "/principal";
                    }
                    else
                    {
                        // Swal.fire({
                        //     icon: "error",
                        //     title: "Oops...",
                        //     text: data.msg,
                        //   });
                        console.log('Entro al else de msg')
                        console.log(data.msg)
                    }
                },
                error: function(xhr, status, error) {
                    console.error(xhr.responseText); // Imprimir la respuesta del servidor en caso de error
                }
            });
        }else{
            Swal.fire({
                icon: "error",
                title: "Oops...",
                text: "Campo vacio",
              });
        }
    });
})


//KEVIN LOGIN PETICION
$(document).ready(function(){
    $('#login_buttonK').click(function(){
        var username = $('#username').val();
        var password = $('#password').val();
        if(username != '' && password != '')
        {
            var dataToSend = JSON.stringify({ username: username, password: password, log: 'valor_del_log' });
            $.ajax({
                url: "http://192.168.111.246:2002/api/iniciarSesionAdmin",
                method: "POST",
                contentType: 'application/json',
                data: dataToSend,
                success: function(data){
                    console.log(data);
                },
                error: function(xhr, status, error) {
                    console.error(xhr.responseText); // Imprimir la respuesta del servidor en caso de error
                }
            });
        }else{
            Swal.fire({
                icon: "error",
                title: "Oops...",
                text: "Campo vacio",
              });
        }
    });
})

//victor LOGIN PETICION
$(document).ready(function(){
    $('#login_buttonV').click(function(){
        var username = $('#username').val();
        var password = $('#password').val();
        if(username != '' && password != '')
        {
            var dataToSend = JSON.stringify({ username: username, password: password, log: 'valor_del_log' });
            $.ajax({
                url: "http://192.168.111.86:8080/mapaGoogle/api/Log/login",
                method: "POST",
                contentType: 'application/json',
                data: dataToSend,
                success: function(data){
                    console.log(data);
                },
                error: function(xhr, status, error) {
                    console.error(xhr.responseText); // Imprimir la respuesta del servidor en caso de error
                }
            });
        }else{
            Swal.fire({
                icon: "error",
                title: "Oops...",
                text: "Campo vacio",
              });
        }
    });
})



//Mi peticion externa
$(document).ready(function(){
    $('#login_buttonI').click(function(){
        var username = $('#username').val();
        var password = $('#password').val();
        if(username != '' && password != '')
        {
            var dataToSend = JSON.stringify({ username: username, password: password, log: 'valor_del_log' });
            $.ajax({
                url: "http://127.0.0.1:5001/action2",
                method: "POST",
                contentType: 'application/json',
                data: dataToSend,
                success: function(data){
                    console.log(data);
                },
                error: function(xhr, status, error) {
                    console.error(xhr.responseText); // Imprimir la respuesta del servidor en caso de error
                }
            });
        }else{
            Swal.fire({
                icon: "error",
                title: "Oops...",
                text: "Campo vacio",
              });
        }
    });
})