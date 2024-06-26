function editarProveedor(id, nombre, telefono, correo, dias, event) {
  document.getElementById("form-id").value = id;
  document.getElementById("form-nombre").value = nombre;
  document.getElementById("form-telefono").value = telefono;
  document.getElementById("form-correo").value = correo;
  document.getElementById("form-diasVisita").value = dias;

  let buttonEditar = document.getElementById("editar");
  buttonEditar.removeAttribute("disabled", "");

  let buttonAdd = document.getElementById("registrar");
  buttonAdd.setAttribute("disabled", "");

  event.preventDefault();
}

document.addEventListener("DOMContentLoaded", function () {
  const editarBtn = document.getElementById("editar");
  const form = document.getElementById("prov-form");

  editarBtn.addEventListener("click", function (event) {
    const nombre = document.getElementById("form-nombre").value;
    const telefono = document.getElementById("form-telefono").value;

    let isValid = true;

    event.preventDefault();
    if (!validarNombre(nombre) || !validarTelefono(telefono)) {
      Swal.fire({
        icon: "error",
        title: "Oops...",
        text: "Verifica que ningún campo esté vacío!",
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
            document.getElementById("form-action").value = "editarProv";

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

function validarNombre(nombre) {
  let isValid = true;
  if (nombre.length === 0) {
    isValid = false;
    return isValid;
  } else {
    isValid = true;
    return isValid;
  }
}
function validarTelefono(telefono) {
  let isValid = true;
  if (telefono.length === 0) {
    isValid = false;
    return isValid;
  } else {
    isValid = true;
    return isValid;
  }
}

function limpiarFormulario() {
  document.getElementById("form-nombre").value = "";
  document.getElementById("form-telefono").value = "";
  document.getElementById("form-correo").value = "";
  document.getElementById("form-diasVisita").value = "";
  let buttonEditar = document.getElementById("editar");
  buttonEditar.setAttribute("disabled", "");

  let buttonAdd = document.getElementById("registrar");
  buttonAdd.removeAttribute("disabled", "");
}

function eliminarProv(id, event) {
  console.log(id);
  // Previene el envío automático del formulario
  event.preventDefault();

  const form = document.getElementById("prov-form");
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
