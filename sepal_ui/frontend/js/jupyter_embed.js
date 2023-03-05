// set a selected map to embed mode (i.e. default display)
var i = 0;
const wait_unitl_element_appear = setInterval(() => {
  var element = document.querySelector(".%s .leaflet-container");
  if (element != null) {
    element.style.position = "";
    element.style.width = "";
    element.style.height = "";
    element.style.zIndex = "";
    element.style.bottom = "";
    element.style.left = "";
    window.dispatchEvent(new Event("resize"));
    clearInterval(wait_unitl_element_appear);
  } else if (i > 50) {
    clearInterval(wait_unitl_element_appear);
    console.log("cannot find the map element");
  } else {
    i++;
  }
}, 100);
