export function init_overlay() {
    console.log("foo");
    document.querySelector("#click-for-overlay").onclick = function () { show_overlay(true); }
    document.querySelector("#comic-page-overlay").onclick = function () { show_overlay(false); }
}

function show_overlay(show) {
    document.querySelector("#comic-page-overlay").hidden = !show;
}
