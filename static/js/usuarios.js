function editarUsuario(id, nombreCompleto, tipousuario, user, password, event) {
  console.log("Hola POpo", id, nombreCompleto, tipousuario, user, password);

  document.getElementById("form-id").value = id;
  document.getElementById("form-nombrecompleto").value = nombreCompleto;
  document.getElementById("form-tipousuario").value = tipousuario;
  document.getElementById("form-username").value = user;
  document.getElementById("form-password").value = password;

  let buttonEditar = document.getElementById("editar");
  buttonEditar.removeAttribute("disabled", "");

  let buttonAdd = document.getElementById("registrar");
  buttonAdd.setAttribute("disabled", "");

  event.preventDefault();
}
//Esta parte es para la validación cuando se va a editar
document.addEventListener("DOMContentLoaded", function () {
  const editarBtn = document.getElementById("editar");
  const form = document.getElementById("user-form");

  editarBtn.addEventListener("click", function (event) {
    const nombrecompleto = document.getElementById("form-nombrecompleto").value;
    const username = document.getElementById("form-username").value;
    const tipousuario = document.getElementById("form-tipousuario").value;
    const password = document.getElementById("form-password").value;

    let isValid = true;

    event.preventDefault();
    if (!validarNombre(nombrecompleto) || !validarUsuarii(username)) {
      Swal.fire({
        icon: "error",
        title: "Oops...",
        text: "Verifica que ningún campo esté vacío!",
      });
      isValid = false;
      event.preventDefault();
    }

    const passwordRegex =
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$/;

    if (!passwordRegex.test(password) || password === "") {
      Swal.fire({
        icon: "error",
        title: "Oops...",
        text: "La contraseña debe tener al menos 6 caracteres, incluyendo una mayúscula, una minúscula, un número y un carácter especial.!",
      });
      isValid = false;
      event.preventDefault();
    }

    // Si todos los campos son válidos, envía el formulario
    // Suponiendo que isValid se calcula en algún lugar antes en tu código
    if (isValid) {
      Swal.fire({
        title: "¿Seguro de editar este usuario?",
        text: "No podrás restablecer la modificación si lo haces!",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Sí, Editar!",
      }).then((result) => {
        if (result.isConfirmed) {
          Swal.fire({
            title: "Editado!",
            text: "Usuario editado correctamente",
            icon: "success",
          }).then(() => {
            document.getElementById("form-action").value = "editarS";

            form.submit(); // Envía el formulario solo después de confirmar la acción
            document.getElementById("form-action").value = "";
          });
        }
        // No necesitas manejar el caso de cancelación aquí porque
        // el formulario no se enviará a menos que se confirme la acción
      });
    } else {
      event.preventDefault(); // Evita enviar el formulario si isValid no es true
    }
  });
});

function validarUsuarii(username) {
  let isValid = true;
  if (username.length === 0) {
    isValid = false;
    return isValid;
  } else {
    isValid = true;
    return isValid;
  }
}
function validarNombre(nombrecompleto) {
  let isValid = true;
  if (nombrecompleto.length === 0) {
    isValid = false;
    return isValid;
  } else {
    isValid = true;
    return isValid;
  }
}

function eliminarUsuari(id, event) {
  // Previene el envío automático del formulario
  event.preventDefault();

  const form = document.getElementById("user-form");
  document.getElementById("form-iddelete").value = id;
  // Asegúrate de que exista un campo para 'eliminar' en tu formulario
  // Por ejemplo, podría ser algo así
  // <input type="hidden" name="action" id="form-action" value="" />

  Swal.fire({
    title: "¿Estás seguro de eliminar este usuario?",
    text: "",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Si, Eliminar!",
  }).then((result) => {
    if (result.isConfirmed) {
      Swal.fire({
        title: "Eliminado!",
        text: "Usuario Eliminado correctamente",
        icon: "success",
      }).then(() => {
        document.getElementById("form-action").value = "eliminar";
        form.submit();
        document.getElementById("form-action").value = "";
      });
    }
  });
}
