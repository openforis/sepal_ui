// set a selected map to fullscreen
var i = 0;
const wait_unitl_element_appear = setInterval(() => {
  var element = document.querySelector(".%s .leaflet-container");
  if (element != null) {
    element.style.position = "fixed";
    element.style.width = "100vw";
    element.style.height = "calc(100vh - %s)";
    element.style.zIndex = 800;
    element.style.bottom = 0;
    element.style.left = 0;
    window.dispatchEvent(new Event("resize"));
    clearInterval(wait_unitl_element_appear);
  } else if (i > 50) {
    clearInterval(wait_unitl_element_appear);
    console.log("cannot find the map element");
  } else {
    i++;
  }
}, 100);
