var visibleNav = true;
function moveNav() {
  moveButton = document.getElementsByClassName("movenavs")[0]
  leftNav = document.getElementsByClassName("leftnav")[0]
  topNav = document.getElementsByClassName("topnav")[0]

  if (visibleNav == true) {
    moveButton.style.left = "0px"
    moveButton.style.transform = "rotate(90deg)"
    leftNav.style.left = "-220px"
    topNav.style.right = "-210px"
    visibleNav = false;
  }
  else {
    moveButton.style.left = "220px";
    moveButton.style.transform = "rotate(-360deg)"
    leftNav.style.left = "10px"
    topNav.style.right = "10px"
    visibleNav = true;
  }


}
