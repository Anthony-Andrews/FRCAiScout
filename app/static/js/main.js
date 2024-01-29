function drawlines() {
    point1 = document.getElementById("point1").getBoundingClientRect();
    point2 = document.getElementById("point2").getBoundingClientRect();
    point3 = document.getElementById("point3").getBoundingClientRect();
    point4 = document.getElementById("point4").getBoundingClientRect();
    lineElement1 = document.getElementById("line1")
    lineElement1.setAttribute("x1", point1.left);
    lineElement1.setAttribute("y1", point1.top);
    lineElement1.setAttribute("x2", point2.left);
    lineElement1.setAttribute("y2", point2.top);
    lineElement2 = document.getElementById("line2")
    lineElement2.setAttribute("x1", point2.left);
    lineElement2.setAttribute("y1", point2.top);
    lineElement2.setAttribute("x2", point3.left);
    lineElement2.setAttribute("y2", point3.top);
    lineElement3 = document.getElementById("line3")
    lineElement3.setAttribute("x1", point3.left);
    lineElement3.setAttribute("y1", point3.top);
    lineElement3.setAttribute("x2", point4.left);
    lineElement3.setAttribute("y2", point4.top );
    lineElement4 = document.getElementById("line4")
    lineElement4.setAttribute("x1", point4.left);
    lineElement4.setAttribute("y1", point4.top);
    lineElement4.setAttribute("x2", point1.left);
    lineElement4.setAttribute("y2", point1.top);
    imgrect = document.getElementById("img").getBoundingClientRect();
    document.getElementById("points").value = ((point1.top - imgrect.top)/imgrect.height) + "," + ((point1.left - imgrect.left)/imgrect.width) + "," +
    ((point2.top - imgrect.top)/imgrect.height) + "," + ((point2.left - imgrect.left)/imgrect.width) + "," +
    ((point3.top - imgrect.top)/imgrect.height) + "," + ((point3.left - imgrect.left)/imgrect.width) + "," +
    ((point4.top - imgrect.top)/imgrect.height) + "," + ((point4.left - imgrect.left)/imgrect.width);
    
}

$(document).ready(function () {
    $("input[type=file]").change(function (event) {
        img = document.getElementById("img")
        img.src = URL.createObjectURL($('#form')[0][0].files[0]);
        document.getElementById("point1") .style.top = "1%"
        document.getElementById("point1") .style.left = "50%"
        document.getElementById("point2") .style.bottom = "50%"
        document.getElementById("point2") .style.left = "50%"
        document.getElementById("point3") .style.top = "50%"
        document.getElementById("point3") .style.right = "1%"
        document.getElementById("point4") .style.bottom = "99%"
        document.getElementById("point4") .style.right = "1%"
        document.getElementById("line1") .style.visibility = "visible"
        document.getElementById("line2") .style.visibility = "visible"
        document.getElementById("line3") .style.visibility = "visible"
        document.getElementById("line4") .style.visibility = "visible"
        drawlines()
    })
    container = null;
    document.getElementById("point1").onmousedown = onMouseDrag;
    document.getElementById("point2").onmousedown = onMouseDrag;
    document.getElementById("point3").onmousedown = onMouseDrag;
    document.getElementById("point4").onmousedown = onMouseDrag;

    function onMouseDrag({ movementX, movementY }) {
        e = window.event
        e.preventDefault();
        pos3 = e.clientX;
        pos4 = e.clientY;
        document.onmouseup = closeDragElement;
        document.onmousemove = elementDrag;
        container = this;
        drawlines()
    }

    function elementDrag(e) {
        e = e || window.event;
        e.preventDefault();
        pos1 = pos3 - e.clientX;
        pos2 = pos4 - e.clientY;
        pos3 = e.clientX;
        pos4 = e.clientY;
        container.style.top = (container.offsetTop - pos2) + "px";
        container.style.left = (container.offsetLeft - pos1) + "px";
        drawlines()
    }

    function closeDragElement() {
        drawlines()
        document.onmouseup = null;
        document.onmousemove = null;
    }
});