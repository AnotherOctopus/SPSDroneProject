
function person() {
    imgname = document.cookie.split("=")[1];
    console.log(imgname);
    $.post("/post",imgname + "=1",()=>{
            console.log("outy");
            window.location.reload();
    });
}
function notperson() {
    imgname = document.cookie.split("=")[1];
    console.log(imgname);
    $.post("/post",imgname + "=0",()=>{
            console.log("outy");
            window.location.reload();
    });
}
