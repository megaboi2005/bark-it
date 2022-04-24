var visibleNav = true;

function moveNav() {
  moveButton = document.getElementById("movenav");
  logo = document.getElementById("logo");
  sidebar = document.getElementById("sidebar");
  sidebutton = document.getElementsByClassName("sidebutton");

  if (visibleNav == true) {
    sidebar.style.width = "150px";
    sidebar.style.height = "auto";
    logo.style.width = "150px";

    for (var i=0;i<sidebutton.length;i+=1){
        sidebutton[i].style.display = 'block';
    }
    visibleNav = false;

  } else {
    sidebar.style.width = "50px";
    logo.style.width = "50px";
    sidebar.style.height = "50px";


    for (var i=0;i<sidebutton.length;i+=1){
        sidebutton[i].style.display = 'none';
    }
    visibleNav = true;
  }
}
