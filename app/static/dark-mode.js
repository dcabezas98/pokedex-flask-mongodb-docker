function change_mode() { // Cambio de modo, almaceno el modo en localStorage
    var mode = localStorage.getItem("mode") || "classic"; // Por defecto se utiliza el modo clásico
    if (mode=="dark")
	mode="classic";
    else
	mode="dark";

    localStorage.setItem("mode", mode);
    set_mode();
}

function set_mode() { // Poner el modo actual
    var mode = localStorage.getItem("mode") || "classic";
    if (mode=="dark")
	document.body.classList.add("dark-mode");
    else
	document.body.classList.remove("dark-mode");
}

set_mode(); // Para que se cargue la página en el modo actual
