var tempInput = document.createElement("input");
tempInput.value = _txt;
document.body.appendChild(tempInput);
tempInput.focus();
tempInput.select();
document.execCommand("copy");
document.body.removeChild(tempInput);
