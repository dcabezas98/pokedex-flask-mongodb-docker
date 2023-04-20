// Para obtener los días de la semana y meses en string
const days=["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
const months=['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

function printTime() { // Captura y formatea la fecha actual
    var d=new Date();
    document.getElementById("date").innerHTML=days[d.getDay()]+" "+d.getDate()+" "+months[d.getMonth()]+" "+d.getFullYear()+", "+d.getHours().toLocaleString('en-US', {
    minimumIntegerDigits: 2, // Dos dígitos enteros para las horas, minutos y segundos
    useGrouping: false
    })+":"+d.getMinutes().toLocaleString('en-US', {
    minimumIntegerDigits: 2,
    useGrouping: false
    })+":"+d.getSeconds().toLocaleString('en-US', {
    minimumIntegerDigits: 2,
    useGrouping: false
    });
}

setInterval(printTime, 1000); // Actualiza cada 1000 milisegundos
